import csv
import random

# ========== MALICIOUS URLs ==========

PHISHING_URLS = [
    "http://g00gle-login.xyz/signin/verify",
    "http://faceb00k-security.tk/account/update",
    "http://paypa1-verify.ml/secure/login",
    "http://amaz0n-order.gq/confirm/password",
    "http://micros0ft-support.cf/auth/credential",
    "http://app1e-id.pw/verify/account",
    "http://192.168.1.1/banking/login.php",
    "http://secure-bank-login.xyz/update/credential",
    "http://netflix-billing.top/account/verify",
    "http://instagram-help.club/password/reset",
    "https://login-verification-required.work/signin",
    "http://account-suspended-verify.click/restore",
]

SCAM_URLS = [
    "https://free-bitcoin-giveaway.xyz/claim",
    "https://crypto-airdrop-double.ml/send-wallet",
    "https://winner-prize-jackpot.tk/claim-reward",
    "https://lottery-winner-2024.gq/get-money",
    "https://free-gift-card-generator.cf/bonus",
    "https://iphone-winner-free.pw/claim-now",
    "https://earn-5000-daily.xyz/signup",
    "https://bitcoin-doubler-legit.top/invest",
    "https://nft-free-airdrop.club/connect-wallet",
    "https://crypto-profit-guaranteed.work/join",
]

MALWARE_URLS = [
    "https://free-download-crack.xyz/photoshop.exe",
    "https://keygen-serial-free.ml/windows-activate",
    "https://game-hack-cheat.tk/download/install",
    "http://update-flash-player.gq/patch.exe",
    "http://antivirus-free-download.cf/scan-fix",
    "https://movie-free-download.pw/video.pdf.exe",
    "http://software-crack-2024.cc/office-keygen",
    "https://driver-update-required.ws/fix-error",
]

SPAM_URLS = [
    "https://wa.me/1234567890",
    "https://t.me/cryptoscamchannel",
    "https://linktr.ee/suspiciousprofile",
    "https://bio.link/fakeinfluencer",
    "https://suspicious-site.carrd.co/",
    "https://beacons.ai/scamprofile",
    "https://bit.ly/3xScAmLnK",
    "https://tinyurl.com/suspicious123",
]

FAKE_SUPPORT_URLS = [
    "http://microsoft-tech-support-helpdesk.xyz/call-now",
    "http://apple-customer-service-help.tk/fix-error",
    "http://amazon-support-urgent.ml/account-issue",
    "http://google-helpdesk-verify.gq/security-alert",
    "http://paypal-customer-support.cf/immediate-action",
]

# ========== SAFE URLs ==========

SAFE_URLS = [
    "https://www.google.com/search?q=weather",
    "https://www.github.com/microsoft/vscode",
    "https://www.amazon.com/dp/B08N5WRWNW",
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://www.wikipedia.org/wiki/Machine_learning",
    "https://www.reddit.com/r/programming",
    "https://www.twitter.com/elonmusk",
    "https://www.linkedin.com/in/satyanadella",
    "https://www.medium.com/@user/article-title",
    "https://www.stackoverflow.com/questions/12345",
    "https://www.nytimes.com/2024/01/15/technology/ai.html",
    "https://www.bbc.com/news/world-us-canada",
    "https://www.netflix.com/browse",
    "https://www.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M",
    "https://www.dropbox.com/s/abc123/document.pdf",
    "https://docs.google.com/document/d/1abc123",
    "https://www.microsoft.com/en-us/windows",
    "https://www.apple.com/iphone",
    "https://www.facebook.com/events/123456",
    "https://www.instagram.com/p/ABC123xyz",
    "https://www.twitch.tv/ninja",
    "https://www.discord.com/invite/abc123",
    "https://www.notion.so/workspace/page",
    "https://www.figma.com/file/abc123/design",
    "https://www.canva.com/design/abc123",
    "https://www.zoom.us/j/1234567890",
    "https://meet.google.com/abc-defg-hij",
    "https://www.paypal.com/invoice/abc123",
    "https://stripe.com/docs/payments",
    "https://www.shopify.com/blog/ecommerce",
]

# ========== GENERATOR FUNCTION ==========

def generate_url_dataset(num_samples=500, output_file="fake_url_dataset.csv"):
    """
    Generate URL dataset for testing
    
    Args:
        num_samples (int): Total samples to generate
        output_file (str): Output CSV filename
    """
    data = []
    
    num_malicious = num_samples // 2
    num_safe = num_samples - num_malicious
    
    malicious_pools = [
        (PHISHING_URLS, "phishing"),
        (SCAM_URLS, "scam"),
        (MALWARE_URLS, "malware"),
        (SPAM_URLS, "spam"),
        (FAKE_SUPPORT_URLS, "phishing"),
    ]
    
    for i in range(num_malicious):
        pool, threat_type = random.choice(malicious_pools)
        url = random.choice(pool)
        
        if random.random() > 0.7:
            url = url.replace("https", "http")
        if random.random() > 0.8:
            url = url + "?ref=" + str(random.randint(1000, 9999))
        
        data.append({
            "id": i + 1,
            "url": url,
            "threat_type": threat_type,
            "label": 1,
            "label_text": "malicious"
        })
    
    for i in range(num_safe):
        url = random.choice(SAFE_URLS)
        
        if random.random() > 0.7:
            url = url + "?utm_source=twitter"
        
        data.append({
            "id": num_malicious + i + 1,
            "url": url,
            "threat_type": "safe",
            "label": 0,
            "label_text": "safe"
        })
    
    random.shuffle(data)
    
    for i, item in enumerate(data):
        item["id"] = i + 1
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["id", "url", "threat_type", "label", "label_text"])
        writer.writeheader()
        writer.writerows(data)
    
    return data