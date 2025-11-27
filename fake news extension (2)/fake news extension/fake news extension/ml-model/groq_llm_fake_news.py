import os
import time
import json
import pandas as pd
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env (if present)
load_dotenv()

# ============ CONFIG ============

INPUT_CSV = "tweets_with_regex_scores.csv"
OUTPUT_CSV = "tweets_with_groq_percentage.csv"
TEXT_COL = "text"
MODEL_NAME = "llama3-8b-8192"

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def classify_with_groq_percentage(text: str, regex_percent: float, regex_tags: str):
    """
    Returns:
        fake_percent: float (0-100)
        reason: str
    """

    if not isinstance(text, str) or text.strip() == "":
        return 0.0, "Empty or invalid text"

    system_prompt = """
You are an AI system that detects fake or misleading news in short social media posts.

You are given:
- Tweet text
- Regex-based fake percentage (0-100)
- Regex tags that matched

Use the regex data as a hint, but make your own judgment.

You must output VALID JSON only in this format:
{
  "fake_percent": <number from 0 to 100>,
  "reason": "<one short sentence explanation>"
}

Guidelines:
- 0 to 25  → very likely real
- 26 to 50 → slightly suspicious
- 51 to 75 → likely fake
- 76 to 100 → highly fake
"""

    user_prompt = {
        "tweet": text,
        "regex_fake_percent": regex_percent,
        "regex_matched_tags": regex_tags
    }

    try:
        chat_completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": json.dumps(user_prompt, ensure_ascii=False)},
            ],
            temperature=0.2,
        )

        raw = chat_completion.choices[0].message.content.strip()
        parsed = json.loads(raw)

        fake_percent = parsed.get("fake_percent", 0)
        reason = parsed.get("reason", "")

        try:
            fake_percent = float(fake_percent)
        except:
            fake_percent = 0.0

        fake_percent = max(0, min(100, fake_percent))

        return fake_percent, reason

    except Exception as e:
        return 0.0, f"Groq error: {e}"


def main():
    df = pd.read_csv(INPUT_CSV)

    required_cols = [TEXT_COL, "regex_fake_percent", "regex_matched_tags"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found. Available: {df.columns.tolist()}")

    groq_fake_percents = []
    groq_reasons = []

    total = len(df)

    for i, row in df.iterrows():
        print(f"[{i+1}/{total}] Processing tweet...")

        percent, reason = classify_with_groq_percentage(
            row[TEXT_COL],
            row["regex_fake_percent"],
            row["regex_matched_tags"]
        )

        groq_fake_percents.append(percent)
        groq_reasons.append(reason)

        time.sleep(0.2)

    df["groq_fake_percent"] = groq_fake_percents
    df["groq_reason"] = groq_reasons

    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\n✅ DONE: Output saved to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
