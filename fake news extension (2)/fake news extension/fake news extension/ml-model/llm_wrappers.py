import os
import base64
import tempfile
from dotenv import load_dotenv

# Load environment
load_dotenv()
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

try:
    from .groq_llm_with_regex_percentage import compute_regex_percent
except Exception:
    compute_regex_percent = None

try:
    from .groq_llm_fake_news import classify_with_groq_percentage
except Exception:
    classify_with_groq_percentage = None

try:
    from .profile_classifier import classify_profile as profile_classify
except Exception:
    profile_classify = None

try:
    from .url_classifier import classify_url as url_classify
except Exception:
    url_classify = None

try:
    from .image_classifier import classify_image as image_classify
except Exception:
    image_classify = None


def score_to_label(score: float):
    if score >= 75:
        return 'FAKE'
    if score >= 50:
        return 'SUSPICIOUS'
    return 'REAL'


def classify_tweet(text: str):
    """Return dict: {'fake_percent', 'reason', 'classification'}"""
    # Use regex percent if available
    regex_percent = 0.0
    regex_tags = []
    if compute_regex_percent:
        try:
            _, regex_percent, regex_tags = compute_regex_percent(text)
        except Exception:
            regex_percent = 0.0

    if classify_with_groq_percentage and GROQ_API_KEY:
        try:
            fake_percent, reason = classify_with_groq_percentage(text, regex_percent, ','.join(regex_tags))
            return {
                'fake_percent': fake_percent,
                'reason': reason,
                'classification': score_to_label(fake_percent)
            }
        except Exception:
            pass

    # Fallback: use regex_percent
    return {
        'fake_percent': regex_percent,
        'reason': 'regex_fallback',
        'classification': score_to_label(regex_percent)
    }


def classify_profile(profile: dict):
    """Return dict from profile classifier wrapper"""
    if profile_classify and GROQ_API_KEY:
        try:
            return profile_classify(profile, GROQ_API_KEY)
        except Exception:
            pass

    # Minimal fallback
    return {
        'classification': 'UNKNOWN',
        'fake_probability': 50,
        'reason': 'no_model_available',
        'regex_score': 0,
        'matched_tags': [],
        'behavioral_flags': []
    }


def classify_url(url: str):
    """Return dict from url classifier wrapper"""
    if url_classify and GROQ_API_KEY:
        try:
            return url_classify(url, GROQ_API_KEY)
        except Exception:
            pass

    return {
        'url': url,
        'classification': 'UNKNOWN',
        'malicious_probability': 50,
        'threat_type': 'unknown',
        'reason': 'no_model_available',
        'regex_score': 0,
        'matched_tags': [],
        'red_flags': [],
        'url_features': {}
    }


def classify_image_base64(image_b64: str, context: str = ''):
    """Accepts base64 image string, saves to temp file and calls image classifier."""
    if not image_b64:
        return {'classification': 'UNKNOWN', 'fake_probability': 50, 'reason': 'no_image'}

    if not image_classify or not GROQ_API_KEY:
        return {'classification': 'UNKNOWN', 'fake_probability': 50, 'reason': 'no_model_available'}

    try:
        b = base64.b64decode(image_b64.split(',')[-1])
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tf:
            tf.write(b)
            temp_path = tf.name

        res = image_classify(temp_path, GROQ_API_KEY, context)
        try:
            os.remove(temp_path)
        except Exception:
            pass
        return res
    except Exception as e:
        return {'classification': 'ERROR', 'fake_probability': 50, 'reason': str(e)}
