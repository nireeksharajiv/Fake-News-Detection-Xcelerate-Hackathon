import pkgutil as _pkgutil
import importlib.util as _importlib_util

# Backwards-compatible shim: newer Python may not expose `pkgutil.get_loader`.
# Flask (and other libs) sometimes call `pkgutil.get_loader`; ensure it exists.
if not hasattr(_pkgutil, 'get_loader'):
    def _get_loader(name):
        spec = _importlib_util.find_spec(name)
        return spec.loader if spec is not None else None
    _pkgutil.get_loader = _get_loader

from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import pickle
import re
from urllib.parse import urlparse
import requests
from PIL import Image
from io import BytesIO
import base64
import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

from flask import send_from_directory

app = Flask('fake_news_api', root_path=os.path.dirname(__file__))
CORS(app)  # Enable CORS for browser extension

# Load ML models
MODEL_DIR = 'models'

class FakeNewsDetector:
    def __init__(self):
        self.text_model = None
        self.url_model = None
        self.profile_model = None
        self.image_model = None
        self.load_models()
        
    def load_models(self):
        """Load all trained ML models"""
        try:
            # Load text classifier (for tweet content)
            if os.path.exists(f'{MODEL_DIR}/text_classifier.pkl'):
                with open(f'{MODEL_DIR}/text_classifier.pkl', 'rb') as f:
                    self.text_model = pickle.load(f)
            
            # Load URL classifier
            if os.path.exists(f'{MODEL_DIR}/url_classifier.pkl'):
                with open(f'{MODEL_DIR}/url_classifier.pkl', 'rb') as f:
                    self.url_model = pickle.load(f)
            
            # Load profile classifier
            if os.path.exists(f'{MODEL_DIR}/profile_classifier.pkl'):
                with open(f'{MODEL_DIR}/profile_classifier.pkl', 'rb') as f:
                    self.profile_model = pickle.load(f)
            
            # Load image classifier
            if os.path.exists(f'{MODEL_DIR}/image_classifier.pkl'):
                with open(f'{MODEL_DIR}/image_classifier.pkl', 'rb') as f:
                    self.image_model = pickle.load(f)
                    
            print("✓ Models loaded successfully")
        except Exception as e:
            print(f"Error loading models: {e}")
    
    def extract_text_features(self, text):
        """Extract features from tweet text using regex patterns"""
        features = {}
        
        # Pattern matching scores
        patterns = {
            'urgency': r'\b(URGENT|BREAKING|ALERT|NOW|MUST SEE|SHOCKING)\b',
            'all_caps': r'\b[A-Z]{5,}\b',
            'clickbait': r'\b(you won\'t believe|doctors hate|one weird trick|what happens next)\b',
            'conspiracy': r'\b(wake up|sheeple|they don\'t want you to know|cover-?up|deep state)\b',
            'unverified': r'\b(reportedly|allegedly|rumored|unconfirmed|sources say)\b',
            'emotional': r'\b(outrageous|disgusting|terrifying|devastating|horrifying)\b',
            'missing_context': r'\b(study shows|research proves|scientists say|experts claim)\b'
        }
        
        text_lower = text.lower()
        
        for pattern_name, pattern in patterns.items():
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            features[f'{pattern_name}_count'] = matches
        
        # Additional features
        features['text_length'] = len(text)
        features['caps_ratio'] = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        features['exclamation_count'] = text.count('!')
        features['question_count'] = text.count('?')
        features['hashtag_count'] = text.count('#')
        features['mention_count'] = text.count('@')
        features['url_count'] = len(re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text))
        features['word_count'] = len(text.split())
        features['avg_word_length'] = np.mean([len(word) for word in text.split()]) if text.split() else 0
        
        return features
    
    def extract_url_features(self, url):
        """Extract features from URL"""
        features = {}
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Domain features
            features['domain_length'] = len(domain)
            features['has_https'] = 1 if parsed.scheme == 'https' else 0
            features['subdomain_count'] = len(domain.split('.')) - 2
            features['path_length'] = len(parsed.path)
            features['has_query'] = 1 if parsed.query else 0
            features['suspicious_tld'] = 1 if any(tld in domain for tld in ['.tk', '.ml', '.ga', '.cf', '.gq']) else 0
            
            # Check if domain is a known news source
            trusted_domains = ['bbc.com', 'nytimes.com', 'reuters.com', 'apnews.com', 
                              'theguardian.com', 'wsj.com', 'washingtonpost.com']
            features['is_trusted_domain'] = 1 if any(td in domain for td in trusted_domains) else 0
            
            # Suspicious patterns in URL
            features['has_ip_address'] = 1 if re.search(r'\d+\.\d+\.\d+\.\d+', domain) else 0
            features['special_char_count'] = len(re.findall(r'[-_@]', url))
            features['digit_count'] = len(re.findall(r'\d', domain))
            
        except Exception as e:
            print(f"Error extracting URL features: {e}")
            features = {k: 0 for k in ['domain_length', 'has_https', 'subdomain_count', 
                                       'path_length', 'has_query', 'suspicious_tld',
                                       'is_trusted_domain', 'has_ip_address', 
                                       'special_char_count', 'digit_count']}
        
        return features
    
    def extract_profile_features(self, profile_data):
        """Extract features from user profile"""
        features = {}
        
        features['follower_count'] = profile_data.get('followers', 0)
        features['following_count'] = profile_data.get('following', 0)
        features['tweet_count'] = profile_data.get('tweets', 0)
        features['is_verified'] = 1 if profile_data.get('verified', False) else 0
        features['has_profile_image'] = 1 if profile_data.get('profile_image', False) else 0
        features['account_age_days'] = profile_data.get('account_age_days', 0)
        
        # Calculate ratios
        if features['follower_count'] > 0:
            features['following_ratio'] = features['following_count'] / features['follower_count']
        else:
            features['following_ratio'] = features['following_count']
        
        # Suspicious patterns
        features['default_profile'] = 1 if not profile_data.get('has_custom_profile', True) else 0
        features['suspicious_username'] = 1 if re.search(r'\d{4,}', profile_data.get('username', '')) else 0
        
        return features
    
    def analyze_text(self, text):
        """Analyze tweet text and return credibility score"""
        features = self.extract_text_features(text)
        
        # Calculate score based on features
        score = 70  # Start neutral-positive
        
        # Deduct for suspicious patterns
        score -= features['urgency_count'] * 5
        score -= features['clickbait_count'] * 8
        score -= features['conspiracy_count'] * 10
        score -= features['unverified_count'] * 3
        score -= features['emotional_count'] * 4
        
        # Deduct for formatting issues
        if features['caps_ratio'] > 0.5:
            score -= 10
        if features['exclamation_count'] > 2:
            score -= features['exclamation_count'] * 2
        
        # Add for quality indicators
        if features['text_length'] > 100:
            score += 5
        if features['url_count'] > 0:
            score += 3
        
        score = max(0, min(100, score))
        
        return {
            'score': score,
            'features': features,
            'flags': self._get_flags_from_features(features)
        }
    
    def analyze_url(self, url):
        """Analyze URL credibility"""
        features = self.extract_url_features(url)
        
        score = 60  # Start neutral
        
        # Add for positive indicators
        if features['has_https']:
            score += 10
        if features['is_trusted_domain']:
            score += 25
        
        # Deduct for suspicious indicators
        if features['suspicious_tld']:
            score -= 20
        if features['has_ip_address']:
            score -= 25
        if features['subdomain_count'] > 2:
            score -= 10
        if features['special_char_count'] > 5:
            score -= 10
        
        score = max(0, min(100, score))
        
        return {
            'score': score,
            'features': features,
            'is_safe': score >= 50
        }
    
    def analyze_profile(self, profile_data):
        """Analyze user profile credibility"""
        features = self.extract_profile_features(profile_data)
        
        score = 50  # Start neutral
        
        # Add for credibility indicators
        if features['is_verified']:
            score += 20
        if features['follower_count'] > 1000:
            score += 10
        if features['account_age_days'] > 365:
            score += 10
        if features['has_profile_image']:
            score += 5
        
        # Deduct for suspicious patterns
        if features['following_ratio'] > 5:
            score -= 15
        if features['default_profile']:
            score -= 10
        if features['suspicious_username']:
            score -= 10
        if features['account_age_days'] < 30:
            score -= 15
        
        score = max(0, min(100, score))
        
        return {
            'score': score,
            'features': features,
            'is_credible': score >= 50
        }
    
    def _get_flags_from_features(self, features):
        """Extract warning flags from features"""
        flags = []
        
        if features.get('urgency_count', 0) > 0:
            flags.append('urgency_language')
        if features.get('clickbait_count', 0) > 0:
            flags.append('clickbait_patterns')
        if features.get('conspiracy_count', 0) > 0:
            flags.append('conspiracy_rhetoric')
        if features.get('unverified_count', 0) > 0:
            flags.append('unverified_claims')
        if features.get('caps_ratio', 0) > 0.5:
            flags.append('excessive_capitalization')
        if features.get('exclamation_count', 0) > 2:
            flags.append('excessive_punctuation')
        if features.get('emotional_count', 0) > 0:
            flags.append('emotional_manipulation')
        
        return flags

# Initialize detector
detector = FakeNewsDetector()

@app.route('/')
def home():
    return jsonify({
        'status': 'online',
        'service': 'Fake News Detection API',
        'version': '1.0',
        'endpoints': {
            '/analyze': 'POST - Analyze tweet content',
            '/analyze-url': 'POST - Analyze URL credibility',
            '/analyze-profile': 'POST - Analyze user profile',
            '/analyze-complete': 'POST - Complete tweet analysis'
        }
    })

@app.route('/analyze', methods=['POST'])
def analyze_tweet():
    """Analyze tweet text for fake news indicators"""
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        result = detector.analyze_text(text)
        
        return jsonify({
            'success': True,
            'analysis': result,
            'trust_level': 'high' if result['score'] >= 70 else 'medium' if result['score'] >= 40 else 'low'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analyze-url', methods=['POST'])
def analyze_url():
    """Analyze URL credibility"""
    try:
        data = request.json
        url = data.get('url', '')
        
        if not url:
            return jsonify({'error': 'No URL provided'}), 400
        
        result = detector.analyze_url(url)
        
        return jsonify({
            'success': True,
            'analysis': result
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analyze-profile', methods=['POST'])
def analyze_profile():
    """Analyze user profile credibility"""
    try:
        data = request.json
        profile_data = data.get('profile', {})
        
        if not profile_data:
            return jsonify({'error': 'No profile data provided'}), 400
        
        result = detector.analyze_profile(profile_data)
        
        return jsonify({
            'success': True,
            'analysis': result
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analyze-complete', methods=['POST'])
def analyze_complete():
    """Complete analysis combining text, URLs, and profile"""
    try:
        data = request.json
        text = data.get('text', '')
        urls = data.get('urls', [])
        profile = data.get('profile', {})
        
        # Analyze each component
        text_result = detector.analyze_text(text) if text else {'score': 50, 'flags': []}
        
        url_scores = []
        for url in urls:
            url_result = detector.analyze_url(url)
            url_scores.append(url_result['score'])
        
        profile_result = detector.analyze_profile(profile) if profile else {'score': 50}
        
        # Calculate weighted combined score
        weights = {'text': 0.5, 'url': 0.3, 'profile': 0.2}
        
        combined_score = (
            text_result['score'] * weights['text'] +
            (np.mean(url_scores) if url_scores else 50) * weights['url'] +
            profile_result['score'] * weights['profile']
        )
        
        combined_score = max(0, min(100, combined_score))
        
        return jsonify({
            'success': True,
            'combined_score': round(combined_score, 2),
            'trust_level': 'high' if combined_score >= 70 else 'medium' if combined_score >= 40 else 'low',
            'components': {
                'text': text_result,
                'urls': url_scores,
                'profile': profile_result
            },
            'flags': text_result['flags'],
            'recommendation': 'safe_to_share' if combined_score >= 70 else 
                            'verify_before_sharing' if combined_score >= 40 else 
                            'do_not_share'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def score_to_label(score):
    if score >= 75:
        return 'FAKE'
    if score >= 50:
        return 'SUSPICIOUS'
    return 'REAL'


@app.route('/api/classify-all', methods=['POST'])
def classify_all_api():
    """Compatibility endpoint for extension: accepts tweet_text, profile, urls, image_base64"""
    try:
        data = request.json or {}

        tweet_text = data.get('tweet_text') or data.get('text') or ''
        profile = data.get('profile') or {}
        urls = data.get('urls') or data.get('url') or []
        image_b64 = data.get('image_base64') or data.get('image') or None

        # Analyze components — prefer LLM wrappers when available
        tweet_res = {'score': 50, 'flags': []}
        profile_res = {'score': 50}

        classify_tweet = classify_profile = classify_url = classify_image_base64 = None
        try:
            import importlib.util
            wrappers_path = os.path.join(os.path.dirname(__file__), 'ml-model', 'llm_wrappers.py')
            if os.path.exists(wrappers_path):
                spec = importlib.util.spec_from_file_location("llm_wrappers", wrappers_path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                classify_tweet = getattr(mod, 'classify_tweet', None)
                classify_profile = getattr(mod, 'classify_profile', None)
                classify_url = getattr(mod, 'classify_url', None)
                classify_image_base64 = getattr(mod, 'classify_image_base64', None)
        except Exception:
            classify_tweet = classify_profile = classify_url = classify_image_base64 = None

        if classify_tweet:
            try:
                t = classify_tweet(tweet_text)
                # wrapper returns fake_percent
                tweet_res = {'score': t.get('fake_percent', 50), 'flags': []}
            except Exception:
                tweet_res = detector.analyze_text(tweet_text) if tweet_text else {'score': 50, 'flags': []}
        else:
            tweet_res = detector.analyze_text(tweet_text) if tweet_text else {'score': 50, 'flags': []}

        if classify_profile:
            try:
                p = classify_profile(profile)
                profile_res = {'score': p.get('fake_probability', p.get('fake_percent', 50))}
            except Exception:
                profile_res = detector.analyze_profile(profile) if profile else {'score': 50}
        else:
            profile_res = detector.analyze_profile(profile) if profile else {'score': 50}

        url_results = []
        for u in (urls or []):
            try:
                if classify_url:
                    ur = classify_url(u)
                    # url_classify returns 'malicious_probability'
                    url_results.append({'score': ur.get('malicious_probability', 50), 'meta': ur})
                else:
                    ur = detector.analyze_url(u)
                    url_results.append({'score': ur.get('score', 50), 'meta': ur})
            except Exception:
                url_results.append({'score': 50, 'meta': {}})

        url_scores = [r.get('score', 50) for r in url_results] if url_results else [50]

        # Image handling: prefer LLM VLM wrapper
        image_result = None
        if image_b64:
            try:
                if classify_image_base64:
                    image_result = classify_image_base64(image_b64, tweet_text)
                else:
                    # fallback to detector.image_model heuristic if present
                    image_data = base64.b64decode(image_b64.split(',')[-1])
                    img = Image.open(BytesIO(image_data)).convert('RGB')
                    if detector.image_model is not None and hasattr(detector.image_model, 'predict'):
                        img_resized = img.resize((224, 224))
                        import numpy as _np
                        arr = _np.array(img_resized) / 255.0
                        try:
                            pred = detector.image_model.predict([arr])
                            if isinstance(pred, (list, tuple)) and len(pred) > 0:
                                score = float(pred[0]) if not isinstance(pred[0], dict) else 50
                            else:
                                score = float(pred)
                            image_result = {'score': max(0, min(100, score)), 'label': score_to_label(score)}
                        except Exception:
                            image_result = {'score': 50, 'label': 'UNKNOWN'}
                    else:
                        image_result = {'score': 50, 'label': 'UNKNOWN'}
            except Exception:
                image_result = {'score': 50, 'label': 'UNKNOWN'}

        # Aggregate overall
        weights = {'text': 0.5, 'url': 0.3, 'profile': 0.2}
        overall_score = (
            tweet_res.get('score', 50) * weights['text'] +
            (sum(url_scores) / len(url_scores)) * weights['url'] +
            profile_res.get('score', 50) * weights['profile']
        )

        overall_score = max(0, min(100, overall_score))

        response = {
            'overall': {
                'classification': score_to_label(overall_score),
                'confidence': round(overall_score)
            },
            'tweet': {
                'classification': score_to_label(tweet_res.get('score', 50)),
                'probability': round(tweet_res.get('score', 50))
            },
            'profile': {
                'classification': score_to_label(profile_res.get('score', 50)),
                'probability': round(profile_res.get('score', 50))
            },
            'urls': [
                {
                    'url': u,
                    'classification': score_to_label(r.get('score', 50)),
                    'probability': round(r.get('score', 50))
                } for u, r in zip(urls if urls else [], url_results if url_results else [{'score':50}])
            ],
            'image': image_result
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'models_loaded': {
            'text_model': detector.text_model is not None,
            'url_model': detector.url_model is not None,
            'profile_model': detector.profile_model is not None,
            'image_model': detector.image_model is not None
        }
    })


@app.route('/debug', methods=['GET'])
def debug_ui():
    """Serve a simple debug UI (static file) to POST to /api/classify-all from the browser."""
    try:
        base = os.path.join(os.path.dirname(__file__), 'web_debug')
        return send_from_directory(base, 'index.html')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create models directory if it doesn't exist
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    print("=" * 50)
    print("🛡️  Fake News Detection API Server")
    print("=" * 50)
    print("\nStarting server on http://localhost:5000")
    print("\nAvailable endpoints:")
    print("  • POST /analyze - Analyze tweet text")
    print("  • POST /analyze-url - Analyze URL")
    print("  • POST /analyze-profile - Analyze profile")
    print("  • POST /analyze-complete - Complete analysis")
    print("  • GET /health - Health check")
    print("\n" + "=" * 50)
    
    app.run(debug=False, host='0.0.0.0', port=5000)