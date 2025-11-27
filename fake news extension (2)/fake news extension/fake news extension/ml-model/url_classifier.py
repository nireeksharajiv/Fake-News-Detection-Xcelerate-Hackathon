import re
import json
from urllib.parse import urlparse
from groq import Groq

# ========== URL REGEX PATTERNS ==========

URL_STRUCTURE_REGEX = {
    "tld_suspicious": r"\.(xyz|top|club|work|click|link|gq|ml|tk|ga|cf|pw|cc|ws)$",
    "ip_address_url": r"https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
    "long_subdomain": r"https?://[a-zA-Z0-9\-]{30,}\.",
    "many_subdomains": r"https?://([a-zA-Z0-9\-]+\.){4,}",
    "url_shortener": r"https?://(bit\.ly|tinyurl\.com|t\.co|goo\.gl|ow\.ly|is\.gd|buff\.ly|short\.link|cutt\.ly|rebrand\.ly)/",
    "unusual_port": r"https?://[^/]+:\d{4,5}/",
    "double_extension": r"\.(pdf|doc|jpg|png)\.(exe|php|html|js)$",
    "encoded_chars": r"%[0-9A-Fa-f]{2}.*%[0-9A-Fa-f]{2}.*%[0-9A-Fa-f]{2}",
    "at_symbol": r"https?://[^/]*@",
    "hyphen_abuse": r"https?://[a-zA-Z0-9]*-{2,}[a-zA-Z0-9]*\.",
}

URL_CONTENT_REGEX = {
    "phishing_keywords": r"(?i)(login|signin|verify|secure|account|update|confirm|password|credential|auth|banking)",
    "scam_keywords": r"(?i)(free-?money|winner|prize|lottery|jackpot|claim|reward|gift-?card|bonus)",
    "crypto_scam": r"(?i)(crypto|bitcoin|btc|eth|wallet|airdrop|token|nft|binance|coinbase).*?(free|claim|double|send)",
    "fake_support": r"(?i)(support|helpdesk|customer-?service|tech-?support|call-?now|fix-?error)",
    "urgency_keywords": r"(?i)(urgent|immediate|act-?now|limited|expire|hurry|fast|quick)",
    "nsfw_url": r"(?i)(xxx|porn|adult|nsfw|sex|nude|onlyfans|18\+)",
    "malware_keywords": r"(?i)(download|install|update|patch|crack|keygen|serial|hack|cheat)",
    "typosquat_google": r"(?i)(g00gle|googel|gooogle|googlle|google[0-9])",
    "typosquat_facebook": r"(?i)(faceb00k|facebok|facebbook|facebook[0-9])",
    "typosquat_amazon": r"(?i)(amaz0n|amazn|amazoon|amazon[0-9])",
    "typosquat_paypal": r"(?i)(paypa1|paypall|paypa[0-9]|pay-?pal[0-9])",
    "typosquat_microsoft": r"(?i)(micros0ft|microsft|mircosoft|microsoft[0-9])",
    "typosquat_apple": r"(?i)(app1e|applle|apple[0-9])",
}

URL_PLATFORM_REGEX = {
    "whatsapp_link": r"https?://(wa\.me|api\.whatsapp\.com|chat\.whatsapp\.com)/",
    "telegram_link": r"https?://(t\.me|telegram\.me|telegram\.org)/",
    "linktree": r"https?://(linktr\.ee|linktree\.com)/",
    "bio_link": r"https?://(bio\.link|instabio\.cc|beacons\.ai|lnk\.bio)/",
    "carrd": r"https?://[A-Za-z0-9\-]+\.carrd\.co/",
    "file_sharing": r"https?://(mega\.nz|mediafire\.com|zippyshare\.com|rapidgator|uploaded\.net)/",
    "paste_site": r"https?://(pastebin\.com|ghostbin\.com|paste\.ee|hastebin\.com)/",
}

# ========== CORE FUNCTIONS ==========

def extract_url_features(url):
    features = {}
    try:
        parsed = urlparse(url)
        features["scheme"] = parsed.scheme
        features["domain"] = parsed.netloc
        features["path"] = parsed.path
        features["query"] = parsed.query
        features["has_https"] = parsed.scheme == "https"
        features["url_length"] = len(url)
        features["domain_length"] = len(parsed.netloc)
        features["path_length"] = len(parsed.path)
        features["num_subdomains"] = parsed.netloc.count('.')
        features["num_hyphens"] = parsed.netloc.count('-')
        features["num_digits_domain"] = sum(c.isdigit() for c in parsed.netloc)
        features["has_port"] = ':' in parsed.netloc.split('@')[-1]
    except:
        features = {"error": "Invalid URL"}
    return features


def check_regex_patterns(url):
    matched_tags = []
    
    for tag, pattern in URL_STRUCTURE_REGEX.items():
        if re.search(pattern, url):
            matched_tags.append(tag)
    
    for tag, pattern in URL_CONTENT_REGEX.items():
        if re.search(pattern, url):
            matched_tags.append(tag)
    
    for tag, pattern in URL_PLATFORM_REGEX.items():
        if re.search(pattern, url):
            matched_tags.append(tag)
    
    total_patterns = len(URL_STRUCTURE_REGEX) + len(URL_CONTENT_REGEX) + len(URL_PLATFORM_REGEX)
    regex_score = min(100, (len(matched_tags) / total_patterns) * 100 * 4)
    
    return regex_score, matched_tags


def check_url_red_flags(url, features):
    flags = []
    
    if not features.get("has_https", True):
        flags.append("no_https")
    if features.get("url_length", 0) > 100:
        flags.append("very_long_url")
    if features.get("num_subdomains", 0) > 3:
        flags.append("too_many_subdomains")
    if features.get("num_hyphens", 0) > 3:
        flags.append("too_many_hyphens")
    if features.get("num_digits_domain", 0) > 3:
        flags.append("many_digits_in_domain")
    if features.get("domain_length", 0) > 30:
        flags.append("very_long_domain")
    if features.get("has_port", False):
        flags.append("has_custom_port")
    
    return flags


def classify_with_groq(url, features, regex_score, tags, red_flags, api_key):
    client = Groq(api_key=api_key)
    
    url_summary = f"""
URL: {url}
Domain: {features.get('domain', 'N/A')}
HTTPS: {features.get('has_https', False)}
URL Length: {features.get('url_length', 0)}
Subdomains: {features.get('num_subdomains', 0)}
"""
    
    prompt = f"""Analyze this URL. Is it MALICIOUS (phishing/scam/malware) or SAFE?

URL ANALYSIS:
{url_summary}

REGEX SCORE: {regex_score:.1f}%
MATCHED PATTERNS: {', '.join(tags) if tags else 'None'}
RED FLAGS: {', '.join(red_flags) if red_flags else 'None'}

Respond ONLY with JSON (no markdown):
{{"malicious_probability": <0-100>, "threat_type": "<phishing|scam|malware|spam|safe>", "reason": "<1-2 sentence explanation>"}}"""
    
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
        return (
            data.get("malicious_probability", 50),
            data.get("threat_type", "unknown"),
            data.get("reason", "No reason")
        )
    except Exception as e:
        print(f"[LLM ERROR] {e}")
        return regex_score, "unknown", "LLM error, using regex score"


def classify_url(url, api_key):
    """
    Main function - call this from your code
    
    Args:
        url (str): URL to analyze
        api_key (str): Groq API key
    
    Returns:
        dict: classification result
    """
    features = extract_url_features(url)
    regex_score, tags = check_regex_patterns(url)
    red_flags = check_url_red_flags(url, features)
    mal_prob, threat_type, reason = classify_with_groq(url, features, regex_score, tags, red_flags, api_key)
    
    if mal_prob >= 70:
        classification = "MALICIOUS"
    elif mal_prob >= 40:
        classification = "SUSPICIOUS"
    else:
        classification = "SAFE"
    
    return {
        "url": url,
        "classification": classification,
        "malicious_probability": mal_prob,
        "threat_type": threat_type,
        "reason": reason,
        "regex_score": round(regex_score, 1),
        "matched_tags": tags,
        "red_flags": red_flags,
        "url_features": features,
    }