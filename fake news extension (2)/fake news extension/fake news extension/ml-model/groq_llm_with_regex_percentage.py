# regex_scoring.py

import re
import pandas as pd

# ============================
# 1. YOUR REGEX PATTERN DICT
# ============================

FAKE_REGEX_RAW = {}

FAKE_REGEX_RAW.update({

    # Emotion-heavy exaggerations
    "extreme_emotion": r"\b(shocking truth|heartbreaking news|terrifying|horrifying|extremely dangerous|unthinkable|catastrophe)\b",

    # Fake political claims
    "political_fake": r"\b(rigged election|fake voting machines|secret bill passed|government collapse|pm/resigned secretly|coup happening)\b",

    # Fake celebrity deaths (VERY common hoax)
    "fake_death": r"\b(has died|passed away suddenly|died in accident|found dead|death hoax|death rumor)\b",

    # Manipulated video/image claims
    "fake_media_claims": r"\b(deepfake|not real footage|edited video|doctored image|fabricated recording)\b",

    # Anti-science / pseudoscience triggers
    "anti_science": r"\b(vaccines kill|earth is flat|hidden cure|scientists lied|fake science|climate change hoax)\b",

    # Fake warnings
    "fake_warning": r"\b(warning issued|avoid this immediately|do not eat this|stop using this product|recall notice circulating)\b",

    # Fake government bans
    "fake_ban": r"\b(banned by govt|govt banned immediately|prohibited by law starting tomorrow|illegal from midnight)\b",

    # Fake emergency alerts
    "fake_emergency": r"\b(red alert|emergency declared|military deployed|curfew from tonight|panic alert)\b",

    # Manipulated statistics
    "manipulated_stats": r"\b(\d{1,3}% increase overnight|skyrocketed by \d{1,3}%|sudden drop of \d{1,3}%|numbers hidden)\b",

    # AI-generated fake style
    "ai_fake_style": r"\b(the truth they fear|everything changes today|revealed after years|hidden for decades)\b",

    # Health conspiracy
    "health_conspiracy": r"\b(cancer cure suppressed|miracle herb|doctors hiding|pharma mafia|virus created in lab secretly)\b",

    # Suspicious miracle product
    "miracle_product": r"\b(lose weight instantly|grow taller in days|hair grows overnight|magic remedy)\b",

    # Scare tactic chain message
    "scare_chain": r"\b(urgent notice|your phone will explode|this message saved lives|read carefully your life depends)\b",

    # Fear manipulation using children
    "child_threat": r"\b(save your children|children in danger|something harming kids|child kidnapping alert)\b",

    # Communal / inflammatory fakes
    "communal_fear": r"\b(attacked by group|religion targeting|community violence started|mass riots)\b",

    # Fake rewards & phishing scams
    "fake_reward": r"\b(win a free car|congratulations you won|click to claim reward|you have been selected)\b",

    # Fake verification
    "fake_verification": r"\b(this is verified|verified message|confirmed by insider|govt insider confirms)\b",

    # Old news resurfaced as new (common hoax)
    "old_news_recycled": r"\b(happened today|just now but from old events)\b",

    # Fake employment scams
    "job_scam": r"\b(earn money from home|instant job|work 1 hour daily|daily payment guaranteed)\b",

    # Fake medical emergencies
    "medical_emergency": r"\b(bleeding from nose due to mobile radiation|new virus outbreak started|dangerous mosquito spreading)\b",

    # Fake communal crime claims
    "communal_crime_fake": r"\b(attacked by migrants|attacked by xyz religion|group targeted on purpose)\b",

    # Fake financial meltdown
    "fake_financial_crisis": r"\b(banks shutting down tomorrow|withdraw all your money|financial system collapsing)\b",

    # Fake food contamination alerts
    "fake_food_alert": r"\b(poison found in food|avoid milk today|contaminated water nationwide)\b",

    # False earthquake/tsunami alerts
    "fake_disaster_alert": r"\b(earthquake predicted tonight|tsunami warning fake|super cyclone will hit your city)\b",

    # Fear of surveillance
    "surveillance_fake": r"\b(secret CCTV everywhere|phones tapped|government listening to calls secretly)\b",

    # Overuse of red flag words commonly seen in misinformation
    "misinfo_keywords": r"\b(fraud|exposed|scam|whistleblower|coverup|truth revealed)\b",

    # Fake historical claims
    "historical_fake": r"\b(hidden history|real history suppressed|truth they never teach)\b",

    # Fake medical miracle claims
    "medical_myth": r"\b(garlic cures everything|drink this for instant cure|avoid vaccines|natural cure works better)\b",

    # Over-appeal to emotions
    "emotional_trigger": r"\b(heart-touching|must read till end|don['’]t ignore this|important for your family)\b",

    # Extreme polarization
    "polarizing_language": r"\b(choose your side|they are the enemy|they want to destroy us)\b",

    # Fake shutdown notification
    "fake_shutdown": r"\b(internet will stop|fb shutting down|twitter closing permanently|whatsapp will charge money)\b",

    # Diseases + miracle solution
    "health_hoax": r"\b(boil this leaf|mix these ingredients|cure in 5 minutes|healed instantly)\b",
})

# ============================
# 2. COMPILE REGEX
# ============================

FAKE_REGEX = {
    name: re.compile(pattern, re.IGNORECASE)
    for name, pattern in FAKE_REGEX_RAW.items()
}

TOTAL_CATEGORIES = len(FAKE_REGEX)


def compute_regex_percent(text: str):
    """
    Returns:
        matched_count: int
        percent: float (0–100)
        matched_keys: list[str]
    """
    if not isinstance(text, str):
        text = str(text)

    matched_keys = []
    for name, pattern in FAKE_REGEX.items():
        if pattern.search(text):
            matched_keys.append(name)

    matched_count = len(matched_keys)
    percent = (matched_count / TOTAL_CATEGORIES) * 100 if TOTAL_CATEGORIES > 0 else 0.0
    return matched_count, round(percent, 2), matched_keys


def main():
    # Change this if your column is named differently (e.g., "Tweet")
    TEXT_COL = "text"

    # Load your extracted tweets
    df = pd.read_csv("tweets_extracted.csv")

    if TEXT_COL not in df.columns:
        raise ValueError(f"Column '{TEXT_COL}' not found in CSV. Available columns: {df.columns.tolist()}")

    regex_counts = []
    regex_percents = []
    regex_tags = []

    for t in df[TEXT_COL]:
        count, percent, tags = compute_regex_percent(t)
        regex_counts.append(count)
        regex_percents.append(percent)
        regex_tags.append(",".join(tags))

    df["regex_match_count"] = regex_counts
    df["regex_fake_percent"] = regex_percents
    df["regex_matched_tags"] = regex_tags

    out_file = "tweets_with_regex_scores.csv"
    df.to_csv(out_file, index=False)
    print(f"[DONE] Saved file with regex scores → {out_file}")


if __name__ == "__main__":
    main()
