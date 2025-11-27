import os
import time
import json
import pandas as pd
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env (if present)
load_dotenv()

# ============ CONFIG ============

INPUT_CSV = "profiles_with_regex_scores.csv"         # from profile_regex_scoring.py
OUTPUT_CSV = "profiles_with_groq_profile_scores.csv"

USERNAME_COL = "username"
DISPLAY_NAME_COL = "display_name"
BIO_COL = "bio"
URL_COL = "url"

MODEL_NAME = "llama3-8b-8192"

# expects: GROQ_API_KEY in environment or passed here directly
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def classify_profile_with_groq(username: str,
                               display_name: str,
                               bio: str,
                               url: str,
                               regex_percent: float,
                               regex_tags: str):
    """
    Returns:
        fake_percent: float (0-100)
        reason: str (short explanation)
    """

    def _safe(x):
        return "" if pd.isna(x) else str(x)

    username = _safe(username)
    display_name = _safe(display_name)
    bio = _safe(bio)
    url = _safe(url)
    regex_tags = _safe(regex_tags)

    try:
        regex_percent = float(regex_percent)
    except Exception:
        regex_percent = 0.0

    system_prompt = """
You are an AI system that detects fake, scammy, or bot-like social media profiles.

You are given:
- username
- display_name
- bio/description text
- profile URL or website
- regex-based fake percent (0–100) from handcrafted rules
- regex tags that matched (which patterns fired)

Use the regex data only as a HINT.
You MUST judge based mainly on the profile fields.

You MUST output VALID JSON only, with this format:

{
  "fake_percent": <number from 0 to 100>,
  "reason": "<one short sentence explanation>"
}

Guidelines (rough, not strict):
- 0–25  → likely real / normal
- 26–50 → somewhat suspicious
- 51–75 → likely fake / spam / bot
- 76–100 → highly suspicious / scam profile
"""

    user_payload = {
        "username": username,
        "display_name": display_name,
        "bio": bio,
        "url": url,
        "profile_regex_fake_percent": regex_percent,
        "profile_regex_tags": regex_tags,
    }

    try:
        chat_completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
            ],
            temperature=0.2,
        )

        raw = chat_completion.choices[0].message.content.strip()
        parsed = json.loads(raw)

        fake_percent = parsed.get("fake_percent", 0)
        reason = parsed.get("reason", "")

        try:
            fake_percent = float(fake_percent)
        except Exception:
            fake_percent = 0.0

        fake_percent = max(0, min(100, fake_percent))  # clamp to 0–100

        return fake_percent, reason or "No reason provided"

    except Exception as e:
        return 0.0, f"Groq error: {e}"


def main():
    if not os.path.exists(INPUT_CSV):
        raise FileNotFoundError(f"Input CSV not found: {INPUT_CSV}")

    df = pd.read_csv(INPUT_CSV)

    required_cols = [
        USERNAME_COL,
        DISPLAY_NAME_COL,
        BIO_COL,
        "profile_fake_percent",
        "profile_regex_tags",
    ]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' missing. Found: {df.columns.tolist()}")

    # URL is optional, fill with "" if missing
    if URL_COL not in df.columns:
        df[URL_COL] = ""

    llm_fake_percents = []
    llm_reasons = []

    total = len(df)
    for i, row in df.iterrows():
        print(f"[{i+1}/{total}] Classifying profile with Groq LLM...")

        fake_percent, reason = classify_profile_with_groq(
            username=row[USERNAME_COL],
            display_name=row[DISPLAY_NAME_COL],
            bio=row[BIO_COL],
            url=row[URL_COL],
            regex_percent=row["profile_fake_percent"],
            regex_tags=row["profile_regex_tags"],
        )

        llm_fake_percents.append(fake_percent)
        llm_reasons.append(reason)

        time.sleep(0.2)  # small delay to be gentle with API

    df["llm_profile_fake_percent"] = llm_fake_percents
    df["llm_profile_reason"] = llm_reasons

    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\n✅ DONE: Saved LLM profile scores to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
