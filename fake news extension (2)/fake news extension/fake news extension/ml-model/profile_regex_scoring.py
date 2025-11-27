import re
import os
import pandas as pd

# ========== 1. REGEX DICTS YOU GAVE ==========

USERNAME_REGEX_EXTRA = {
    # Looks like random junk (letters+digits, no clear word)
    "username_random_junk": r"^(?!(support|help|crypto|official|real)$)[A-Za-z0-9]{8,}$",

    # Starts or ends with many digits (common bot/scam)
    "username_digit_prefix": r"^\d{3,}[A-Za-z_]+$",
    "username_digit_suffix": r"^[A-Za-z_]+\d{3,}$",

    # Contains "news" or "update" like a fake news/alerts account
    "username_fake_news": r"(?i)^\w*(news|alerts?|update|breaking)\w*$",

    # Contains "bot" or "auto" indicating automation
    "username_bot_like": r"(?i)^\w*(bot|auto|autopost)\w*$",

    # Repeated letters (spammy feel) like "loooovee", "freeee"
    "username_repeated_chars": r".([A-Za-z0-9])\1\1+.",

    # Promo / marketing style usernames
    "username_marketing": r"(?i)^\w*(marketing|promo|deals?|discounts?|offers?)\w*$",

    # Forex / trading scam handles
    "username_trading_scam": r"(?i)^\w*(trader|forex|signals?|pips|options|derivatives)\w*$",

    # Adult / NSFW spam
    "username_nsfw": r"(?i)^\w*(xxx|nsfw|onlyfans|18\+|nude|hotgirl|hotboy)\w*$",
}

DISPLAY_NAME_REGEX_EXTRA = {
    # "CEO of", "Founder of", etc. in casual accounts
    "display_fake_role": r"(?i)\b(ceo|founder|owner|director)\s+of\b",

    # Multiple emojis + no clear words
    "display_mostly_emoji": r"^(?:[\U0001F300-\U0001F6FF\U0001F900-\U0001F9FF]\s*){3,}$",

    # “Giveaway”, “Free”, “Win” in display name
    "display_giveaway": r"(?i)\b(giveaway|free|win|prize|jackpot|lottery)\b",

    # “Fan account”, “parody” (could still be flag)
    "display_fan_parody": r"(?i)\b(fan\s*account|parody|backup)\b",

    # Crypto signals / investments
    "display_crypto_trader": r"(?i)\b(crypto trader|forex signals?|investment expert|profit daily)\b",
}

BIO_REGEX_FAKE = {
    # DM / inbox for services (often scammy)
    "bio_dm_for": r"(?i)\b(dm|inbox|message)\s+(for|me for)\s+(details|collab|promo|signals|investment|trading)\b",

    # Fast money / guaranteed income
    "bio_fast_money": r"(?i)\b(earn|make)\s+\$?\d+\s+(per day|daily|every day|per hour)\b",
    "bio_no_risk_profit": r"(?i)\b(no risk|guaranteed profit|sure profit|100% profit)\b",

    # Crypto / forex hype
    "bio_crypto_promo": r"(?i)\b(crypto|bitcoin|btc|eth|forex|nft|binance|bybit)\b.*\b(signals?|profits?|returns?)\b",

    # Contact via WhatsApp / Telegram
    "bio_whatsapp_contact": r"(?i)\b(whatsapp|wa\.me|message me on wa)\b",
    "bio_telegram_contact": r"(?i)\b(telegram|t\.me/|join my channel)\b",

    # Fake support / helpdesk in bio
    "bio_fake_support": r"(?i)\b(official support|customer support|helpdesk|24/7 support)\b",

    # Shady disclaimers
    "bio_disclaimer_shady": r"(?i)\b(not responsible for any loss|trade at your own risk)\b",

    # “Not affiliated…” but posing like official
    "bio_not_affiliated": r"(?i)\b(not affiliated with|unofficial|fan made)\b",

    # Follow/gain spam
    "bio_follow_gain": r"(?i)\b(follow back|follow4follow|f4f|gain\s+followers)\b",

    # Link in bio pattern
    "bio_link_in_bio": r"(?i)\b(link in bio|check my bio link|tap the link)\b",

    # NSFW / adult
    "bio_nsfw": r"(?i)\b(18\+|nsfw|onlyfans|nudes|adult content)\b",

    # Over-claim authority
    "bio_fake_authority": r"(?i)\b(official page of|real account of|only real account|verified by)\b",

    # Typical scammy phrases
    "bio_scammy_phrases": r"(?i)\b(double your money|send me and I will|investment plan|dm for investment)\b",

    # Fake giveaway prompts
    "bio_giveaway_scam": r"(?i)\b(daily giveaways|retweet for a chance to win|send wallet address)\b",
}

URL_REGEX_FAKE = {
    "url_whatsapp": r"https?://(wa\.me|api\.whatsapp\.com)/",
    "url_telegram": r"https?://(t\.me|telegram\.me)/",

    # Link aggregators
    "url_linktree": r"https?://(linktr\.ee|linktree\.com)/",
    "url_carrd": r"https?://[A-Za-z0-9\-]+\.carrd\.co/",
    "url_biorelink": r"https?://(bio\.link|instabio\.cc|beacons\.ai)/",

    # Crypto / quick profit landing pages
    "url_crypto_landing": r"https?://[A-Za-z0-9\.\-]+/(crypto|bitcoin|btc|eth|nft|forex|signals|investment|profit)",

    # Fake support-like
    "url_fake_support_like": r"https?://[A-Za-z0-9\.\-]+/(support|helpdesk|customerservice|customer-support)",
}

PROFILE_LANGUAGE_HINTS = {
    "bio_worldwide": r"(?i)\b(worldwide|global service|service all over the world)\b",
    "bio_247": r"(?i)\b(24/7|24x7)\b.*\b(support|signals?|trading|online)\b",
}

# ========== 2. COMPILE ALL PATTERNS ==========

USERNAME_REGEX = {k: re.compile(v) for k, v in USERNAME_REGEX_EXTRA.items()}
DISPLAY_REGEX = {k: re.compile(v) for k, v in DISPLAY_NAME_REGEX_EXTRA.items()}
BIO_REGEX = {k: re.compile(v) for k, v in BIO_REGEX_FAKE.items()}
URL_REGEX = {k: re.compile(v) for k, v in URL_REGEX_FAKE.items()}
LANG_REGEX = {k: re.compile(v) for k, v in PROFILE_LANGUAGE_HINTS.items()}

TOTAL_PATTERNS = (
    len(USERNAME_REGEX)
    + len(DISPLAY_REGEX)
    + len(BIO_REGEX)
    + len(URL_REGEX)
    + len(LANG_REGEX)
)


def _safe_str(x):
    return "" if pd.isna(x) else str(x)


def compute_profile_regex_score(username, display_name, bio, url):
    """
    Returns:
      matched_count: int
      fake_percent: float (0–100)
      matched_tags: list[str]
    """
    username = _safe_str(username)
    display_name = _safe_str(display_name)
    bio = _safe_str(bio)
    url = _safe_str(url)

    matched = []

    for name, pattern in USERNAME_REGEX.items():
        if pattern.search(username):
            matched.append(name)

    for name, pattern in DISPLAY_REGEX.items():
        if pattern.search(display_name):
            matched.append(name)

    for name, pattern in BIO_REGEX.items():
        if pattern.search(bio):
            matched.append(name)

    for name, pattern in URL_REGEX.items():
        if pattern.search(url):
            matched.append(name)

    # language hints check on bio too
    for name, pattern in LANG_REGEX.items():
        if pattern.search(bio):
            matched.append(name)

    matched_count = len(matched)
    fake_percent = (matched_count / TOTAL_PATTERNS) * 100 if TOTAL_PATTERNS > 0 else 0.0
    return matched_count, round(fake_percent, 2), matched


def main():
    # 👉 CHANGE THESE TO MATCH YOUR CSV COLUMN NAMES
    INPUT_CSV = "profiles_extracted.csv"       # your input with profile info
    OUTPUT_CSV = "profiles_with_regex_scores.csv"

    USERNAME_COL = "username"
    DISPLAY_NAME_COL = "display_name"
    BIO_COL = "bio"
    URL_COL = "url"        # can be profile link / website / first URL

    if not os.path.exists(INPUT_CSV):
        raise FileNotFoundError(f"{INPUT_CSV} not found")

    df = pd.read_csv(INPUT_CSV)

    for col in [USERNAME_COL, DISPLAY_NAME_COL, BIO_COL]:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' missing in CSV. Found: {df.columns.tolist()}")

    # URL column is optional
    if URL_COL not in df.columns:
        df[URL_COL] = ""

    match_counts = []
    fake_percents = []
    match_tags_list = []
    

    for _, row in df.iterrows():
        username = row[USERNAME_COL]
        display = row[DISPLAY_NAME_COL]
        bio = row[BIO_COL]
        url = row[URL_COL]

        count, percent, tags = compute_profile_regex_score(username, display, bio, url)
        match_counts.append(count)
        fake_percents.append(percent)
        match_tags_list.append(",".join(tags))

    df["profile_regex_match_count"] = match_counts
    df["profile_fake_percent"] = fake_percents
    df["profile_regex_tags"] = match_tags_list

    df.to_csv(OUTPUT_CSV, index=False)
    print(f"[DONE] Saved: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
