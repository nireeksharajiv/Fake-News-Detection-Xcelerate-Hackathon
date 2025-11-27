import re
import os
import json
from groq import Groq

# ========== REGEX PATTERNS ==========

USERNAME_REGEX = {
    "username_random_junk": r"^(?!(support|help|crypto|official|real)$)[A-Za-z0-9]{8,}$",
    "username_digit_prefix": r"^\d{3,}[A-Za-z_]+$",
    "username_digit_suffix": r"^[A-Za-z_]+\d{3,}$",
    "username_fake_news": r"(?i)^\w*(news|alerts?|update|breaking)\w*$",
    "username_bot_like": r"(?i)^\w*(bot|auto|autopost)\w*$",
    "username_repeated_chars": r"(.)\1\1+",
    "username_marketing": r"(?i)^\w*(marketing|promo|deals?|discounts?|offers?)\w*$",
    "username_trading_scam": r"(?i)^\w*(trader|forex|signals?|pips|options|derivatives)\w*$",
    "username_nsfw": r"(?i)^\w*(xxx|nsfw|onlyfans|18\+|nude|hotgirl|hotboy)\w*$",
}

DISPLAY_NAME_REGEX = {
    "display_fake_role": r"(?i)\b(ceo|founder|owner|director)\s+of\b",
    "display_mostly_emoji": r"[\U0001F300-\U0001F6FF\U0001F900-\U0001F9FF]{3,}",
    "display_giveaway": r"(?i)\b(giveaway|free|win|prize|jackpot|lottery)\b",
    "display_fan_parody": r"(?i)\b(fan\s*account|parody|backup)\b",
    "display_crypto_trader": r"(?i)\b(crypto trader|forex signals?|investment expert|profit daily)\b",
}

BIO_REGEX = {
    "bio_dm_for": r"(?i)\b(dm|inbox|message)\s+(for|me for)\s+(details|collab|promo|signals|investment|trading)\b",
    "bio_fast_money": r"(?i)\b(earn|make)\s+\$?\d+\s+(per day|daily|every day|per hour)\b",
    "bio_no_risk_profit": r"(?i)\b(no risk|guaranteed profit|sure profit|100% profit)\b",
    "bio_crypto_promo": r"(?i)\b(crypto|bitcoin|btc|eth|forex|nft|binance|bybit)\b.*\b(signals?|profits?|returns?)\b",
    "bio_whatsapp_contact": r"(?i)\b(whatsapp|wa\.me|message me on wa)\b",
    "bio_telegram_contact": r"(?i)\b(telegram|t\.me/|join my channel)\b",
    "bio_fake_support": r"(?i)\b(official support|customer support|helpdesk|24/7 support)\b",
    "bio_disclaimer_shady": r"(?i)\b(not responsible for any loss|trade at your own risk)\b",
    "bio_not_affiliated": r"(?i)\b(not affiliated with|unofficial|fan made)\b",
    "bio_follow_gain": r"(?i)\b(follow back|follow4follow|f4f|gain\s+followers)\b",
    "bio_link_in_bio": r"(?i)\b(link in bio|check my bio link|tap the link)\b",
    "bio_nsfw": r"(?i)\b(18\+|nsfw|onlyfans|nudes|adult content)\b",
    "bio_fake_authority": r"(?i)\b(official page of|real account of|only real account|verified by)\b",
    "bio_scammy_phrases": r"(?i)\b(double your money|send me and I will|investment plan|dm for investment)\b",
    "bio_giveaway_scam": r"(?i)\b(daily giveaways|retweet for a chance to win|send wallet address)\b",
}

URL_REGEX = {
    "url_whatsapp": r"https?://(wa\.me|api\.whatsapp\.com)/",
    "url_telegram": r"https?://(t\.me|telegram\.me)/",
    "url_linktree": r"https?://(linktr\.ee|linktree\.com)/",
    "url_carrd": r"https?://[A-Za-z0-9\-]+\.carrd\.co/",
    "url_biorelink": r"https?://(bio\.link|instabio\.cc|beacons\.ai)/",
    "url_crypto_landing": r"https?://[A-Za-z0-9\.\-]+/(crypto|bitcoin|btc|eth|nft|forex|signals|investment|profit)",
    "url_fake_support_like": r"https?://[A-Za-z0-9\.\-]+/(support|helpdesk|customerservice|customer-support)",
}

# ========== CORE FUNCTIONS ==========

def check_regex_patterns(profile):
    """Run all regex patterns and return matched tags + score"""
    matched_tags = []
    
    username = profile.get("username", "") or ""
    display_name = profile.get("display_name", "") or ""
    bio = profile.get("bio", "") or ""
    url = profile.get("url", "") or ""
    
    for tag, pattern in USERNAME_REGEX.items():
        if re.search(pattern, username):
            matched_tags.append(tag)
    
    for tag, pattern in DISPLAY_NAME_REGEX.items():
        if re.search(pattern, display_name):
            matched_tags.append(tag)
    
    for tag, pattern in BIO_REGEX.items():
        if re.search(pattern, bio):
            matched_tags.append(tag)
    
    for tag, pattern in URL_REGEX.items():
        if re.search(pattern, url):
            matched_tags.append(tag)
    
    total_patterns = len(USERNAME_REGEX) + len(DISPLAY_NAME_REGEX) + len(BIO_REGEX) + len(URL_REGEX)
    regex_score = min(100, (len(matched_tags) / total_patterns) * 100 * 3)
    
    return regex_score, matched_tags


def check_behavioral_signals(profile):
    """Check behavioral red flags"""
    flags = []
    
    followers = profile.get("followers_count", 0) or 0
    following = profile.get("following_count", 0) or 0
    tweets = profile.get("tweet_count", 0) or 0
    account_age = profile.get("account_age_days", 365) or 365
    has_image = profile.get("has_profile_image", True)
    has_banner = profile.get("has_banner", True)
    
    if following > 0 and followers / max(following, 1) < 0.1:
        flags.append("low_follower_ratio")
    
    if account_age < 30:
        flags.append("very_new_account")
    elif account_age < 90:
        flags.append("new_account")
    
    if not has_image:
        flags.append("no_profile_image")
    
    if not has_banner:
        flags.append("no_banner")
    
    if account_age > 30 and tweets < 10:
        flags.append("low_activity")
    
    if following > 5000:
        flags.append("mass_following")
    
    return flags


def classify_with_groq(profile, regex_score, tags, behavioral_flags, api_key):
    """Send to Groq LLM for final classification"""
    client = Groq(api_key=api_key)
    
    profile_summary = f"""
Username: {profile.get('username', '')}
Display Name: {profile.get('display_name', '')}
Bio: {profile.get('bio', '')}
URL: {profile.get('url', '')}
Followers: {profile.get('followers_count', 0)}
Following: {profile.get('following_count', 0)}
Tweets: {profile.get('tweet_count', 0)}
Account Age (days): {profile.get('account_age_days', 0)}
Verified: {profile.get('verified', False)}
"""
    
    prompt = f"""Analyze this Twitter profile. Is it FAKE (spam/scam/bot) or REAL?

PROFILE:
{profile_summary}

REGEX SCORE: {regex_score:.1f}%
MATCHED PATTERNS: {', '.join(tags) if tags else 'None'}
BEHAVIORAL FLAGS: {', '.join(behavioral_flags) if behavioral_flags else 'None'}

Respond ONLY with JSON (no markdown):
{{"fake_probability": <0-100>, "reason": "<1-2 sentence explanation>"}}"""
    
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=200,
        )
        
        result = response.choices[0].message.content.strip()
        result = result.replace("```json", "").replace("```", "").strip()
        data = json.loads(result)
        return data.get("fake_probability", 50), data.get("reason", "No reason")
    
    except Exception as e:
        print(f"[LLM ERROR] {e}")
        return regex_score, "LLM error, using regex score"


def classify_profile(profile, api_key):
    """
    Main classification function - call this from your code
    
    Args:
        profile (dict): Profile data with keys:
            - username, display_name, bio, url
            - followers_count, following_count, tweet_count
            - account_age_days, has_profile_image, has_banner, verified
        api_key (str): Groq API key
    
    Returns:
        dict: {
            "classification": "REAL" | "SUSPICIOUS" | "FAKE",
            "fake_probability": 0-100,
            "reason": "explanation string",
            "regex_score": 0-100,
            "matched_tags": [...],
            "behavioral_flags": [...]
        }
    """
    # Step 1: Regex analysis
    regex_score, tags = check_regex_patterns(profile)
    
    # Step 2: Behavioral analysis
    behavioral_flags = check_behavioral_signals(profile)
    
    # Step 3: LLM classification
    fake_prob, reason = classify_with_groq(profile, regex_score, tags, behavioral_flags, api_key)
    
    # Step 4: Final classification
    if fake_prob >= 70:
        classification = "FAKE"
    elif fake_prob >= 40:
        classification = "SUSPICIOUS"
    else:
        classification = "REAL"
    
    return {
        "classification": classification,
        "fake_probability": fake_prob,
        "reason": reason,
        "regex_score": round(regex_score, 1),
        "matched_tags": tags,
        "behavioral_flags": behavioral_flags,
    }