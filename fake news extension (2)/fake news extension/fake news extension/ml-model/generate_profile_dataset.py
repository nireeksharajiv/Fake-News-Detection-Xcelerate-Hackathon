import csv
import random

# ========== FAKE PROFILES (will trigger your regex patterns) ==========

FAKE_USERNAMES = [
    "cryptoking8847291", "forex_signals_pro", "btc_trader99821", "auto_news_bot",
    "breaking_alerts247", "freeeemoney", "officialcryptohelp", "trading_bot_auto",
    "jackpot_winner2024", "nft_profits_daily", "bitcoin_doubler", "signals_forex123",
    "marketing_deals_pro", "promo_offers_daily", "hot_trader_xxx", "binance_support_help",
    "realcryptotrader", "profits_guaranteed", "daily_giveaway_win", "news_updates_alert",
    "83aborhan", "john827319423", "xxxhotdeals", "autopost_news", "loooovecrypto",
    "helpdesk_official", "support_247_help", "forex_pips_master", "eth_btc_signals",
    "onlyfans_promo99", "discounts_daily", "trading_derivatives", "nsfw_content18",
]

FAKE_DISPLAY_NAMES = [
    "🚀 CEO of CryptoGains 🚀", "💰 Forex Signals Expert 💰", "🎁 FREE GIVEAWAY 🎁",
    "💎 Bitcoin Millionaire 💎", "🔥 Profit Daily Guaranteed 🔥", "⚡ Crypto Trader Pro ⚡",
    "🎰 Win Big Jackpot 🎰", "💵 Investment Expert 💵", "🌟 Founder of TradePro 🌟",
    "🎉 Daily Giveaways 🎉", "💸 Make $5000/Day 💸", "🏆 Prize Winner Official 🏆",
    "Fan Account (Parody)", "Backup Account", "💎💎💎💎💎", "🚀🌙💰🔥⚡",
    "Director of Global Trading", "Owner of CryptoVault", "Real Elon Fan Account",
]

FAKE_BIOS = [
    "DM for crypto signals 📈 Make $500 daily guaranteed! WhatsApp: wa.me/123456",
    "🚀 Earn $1000 per day with my trading signals! No risk, 100% profit! t.me/fakesignals",
    "Official support for Binance users. DM for help 24/7. Not affiliated with Binance.",
    "Crypto trader | Forex signals | Guaranteed profit | DM for investment plans 💰",
    "Send me 0.1 BTC and I will send back 1 BTC! Double your money! 🎁",
    "Follow4follow | F4F | Gain followers fast! Link in bio for free followers!",
    "18+ | OnlyFans creator | NSFW content | Adult only 🔞 Check my bio link!",
    "Investment expert | Make $2000 per hour | WhatsApp for details | No risk profit",
    "Daily giveaways! Retweet for a chance to win $1000! Send wallet address to claim!",
    "Telegram: t.me/cryptoprofits | Join my channel for FREE trading signals!",
    "Real account of famous trader | Verified by community | Only real account!",
    "24/7 customer support | Helpdesk | Message me on WA for instant help",
    "Forex signals | Bitcoin profits | Trade at your own risk | Not responsible for any loss",
    "DM me for collab | Promo | Marketing services | Fast money guaranteed!",
    "Official page of CryptoKing | Global service | 24/7 trading signals worldwide",
    "Tap the link in bio! 🔗 Free crypto! Investment plan available! DM for details!",
]

FAKE_URLS = [
    "https://wa.me/1234567890", "https://t.me/cryptoscam", "https://linktr.ee/fakesignals",
    "https://bio.link/cryptoking", "https://beacons.ai/faketrader", "https://mysite.carrd.co/",
    "https://cryptoprofit.com/signals", "https://btc-doubler.net/investment",
    "https://forex-signals-pro.com/profit", "https://fake-support.com/helpdesk",
    "https://telegram.me/scamchannel", "https://instabio.cc/fakeprofile",
]

# ========== REAL PROFILES (normal, legitimate users) ==========

REAL_USERNAMES = [
    "john_smith", "sarah_jones", "mike_photography", "emma_travels", "david_codes",
    "lisa_writes", "alex_music", "chris_design", "rachel_fitness", "tom_gaming",
    "anna_foodie", "james_tech", "sophia_art", "daniel_sports", "olivia_books",
    "ryan_movies", "grace_yoga", "kevin_outdoors", "megan_pets", "brian_coffee",
    "jennifer_diy", "andrew_cars", "ashley_garden", "steven_cooking", "nicole_fashion",
    "matthew_hiking", "amanda_dance", "joshua_science", "stephanie_music", "tyler_photo",
]

REAL_DISPLAY_NAMES = [
    "John Smith", "Sarah Jones", "Mike Photography", "Emma | Travel Blogger",
    "David - Software Dev", "Lisa Writes", "Alex 🎵", "Chris Design Studio",
    "Rachel | Fitness Coach", "Tom Gaming", "Anna Foodie", "James Tech Reviews",
    "Sophia Art", "Daniel Sports Fan", "Olivia 📚", "Ryan Movie Buff",
    "Grace Yoga", "Kevin Outdoors", "Megan 🐕", "Brian ☕", "Jennifer DIY",
    "Andrew", "Ashley Garden Life", "Steven Cooks", "Nicole Fashion",
]

REAL_BIOS = [
    "Software developer | Coffee lover | Building cool stuff",
    "Travel enthusiast 🌍 | 25 countries and counting | Photography",
    "Mom of 2 | Book lover | Trying to figure out life one day at a time",
    "Graphic designer based in NYC | Available for freelance work",
    "Fitness coach | Helping people reach their goals | DMs open for coaching inquiries",
    "Writer | Blogger | Sharing stories and experiences",
    "Music producer | Guitar player | Living for the weekends",
    "Tech enthusiast | Reviewing gadgets | Opinions are my own",
    "Plant parent 🌱 | Yoga practitioner | Mindfulness advocate",
    "Sports fan | Lakers forever | Fantasy football addict",
    "Home cook | Recipe developer | Food photography",
    "Student | Learning every day | Future engineer",
    "Artist | Painter | Commissions open | Portfolio in link",
    "Dad jokes enthusiast | IT professional | Weekend warrior",
    "Bookworm | Currently reading: too many books | Recommendations welcome",
    "Movie reviewer | Cinephile | No spoilers please",
    "Outdoor adventurer | Hiker | Nature photographer",
    "Pet lover | Rescue advocate | My dog runs this account",
    "Coffee snob | Remote worker | Digital nomad wannabe",
    "DIY projects | Home improvement | Learning as I go",
]

REAL_URLS = [
    "https://johndoe.com", "https://linkedin.com/in/sarahjones", "https://github.com/mikecoder",
    "https://medium.com/@emmawrites", "https://youtube.com/davidtech", "https://instagram.com/lisaart",
    "https://twitter.com/alexmusic", "https://behance.net/chrisdesign", "https://rachelfitness.com",
    "", "", "",  # Many real users don't have URLs
]

def generate_fake_profile():
    return {
        "username": random.choice(FAKE_USERNAMES),
        "display_name": random.choice(FAKE_DISPLAY_NAMES),
        "bio": random.choice(FAKE_BIOS),
        "url": random.choice(FAKE_URLS) if random.random() > 0.3 else "",
        "followers": random.randint(10, 5000),
        "following": random.randint(500, 10000),  # Often follow many, few followers
        "tweets": random.randint(50, 500),
        "account_age_days": random.randint(1, 90),  # Usually new accounts
        "has_profile_image": random.choice([True, False]),
        "has_banner": random.choice([True, False, False]),  # Often no banner
        "verified": False,
        "label": 1,
        "label_text": "fake"
    }

def generate_real_profile():
    followers = random.randint(50, 50000)
    return {
        "username": random.choice(REAL_USERNAMES),
        "display_name": random.choice(REAL_DISPLAY_NAMES),
        "bio": random.choice(REAL_BIOS),
        "url": random.choice(REAL_URLS),
        "followers": followers,
        "following": random.randint(100, min(followers * 2, 2000)),  # Balanced ratio
        "tweets": random.randint(100, 10000),
        "account_age_days": random.randint(180, 3650),  # Older accounts
        "has_profile_image": True,
        "has_banner": random.choice([True, True, False]),  # Usually have banner
        "verified": random.random() > 0.95,  # Rare verification
        "label": 0,
        "label_text": "real"
    }

def generate_dataset(num_samples=500, output_file="fake_profile_dataset.csv"):
    data = []
    
    num_fake = num_samples // 2
    num_real = num_samples - num_fake
    
    # Generate fake profiles
    for i in range(num_fake):
        profile = generate_fake_profile()
        profile["id"] = i + 1
        data.append(profile)
    
    # Generate real profiles
    for i in range(num_real):
        profile = generate_real_profile()
        profile["id"] = num_fake + i + 1
        data.append(profile)
    
    # Shuffle
    random.shuffle(data)
    
    # Reassign IDs after shuffle
    for i, item in enumerate(data):
        item["id"] = i + 1
    
    # Write to CSV
    fieldnames = ["id", "username", "display_name", "bio", "url", "followers", 
                  "following", "tweets", "account_age_days", "has_profile_image", 
                  "has_banner", "verified", "label", "label_text"]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"✅ Generated {num_samples} profile samples")
    print(f"   - Fake profiles: {num_fake}")
    print(f"   - Real profiles: {num_real}")
    print(f"   - Saved to: {output_file}")
    
    # Show sample
    print("\n📋 Sample fake profile:")
    fake_sample = [d for d in data if d["label"] == 1][0]
    for k, v in fake_sample.items():
        print(f"   {k}: {v}")

if __name__ == "__main__":
    generate_dataset(500, "fake_profile_dataset.csv")