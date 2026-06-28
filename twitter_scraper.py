import requests
from bs4 import BeautifulSoup
from datetime import datetime

# ── Nitter instances — tries each one until one works ────────────────────────
NITTER_INSTANCES = [
    "https://nitter.poast.org",
    "https://nitter.privacydev.net",
    "https://nitter.catsarch.com",
    "https://nitter.woodland.cafe",
]

# ── Accounts to monitor ───────────────────────────────────────────────────────
TWITTER_ACCOUNTS = [
    ("TrumpTruthOnX",  "Trump"),
    ("federalreserve",   "Federal Reserve"),
    ("KitcoNewsNOW",     "Kitco News"),
    ("zerohedge",        "ZeroHedge"),
    ("unusual_whales",   "Unusual Whales"),
    ("axios",            "Axios"),
    ("Reuters",          "Reuters"),
    ("markets",          "Bloomberg Markets"),
]

# ── Keywords: tweet must contain at least one ─────────────────────────────────
GOLD_KEYWORDS = [
    "gold", "xau", "bullion", "safe haven", "precious metal",
    "tariff", "trade war", "trade deal", "sanction", "embargo",
    "federal reserve", "fed rate", "powell", "fomc", "rate cut", "rate hike",
    "interest rate", "inflation", "cpi", "pce",
    "dollar", "dxy", "usd strength",
    "war", "airstrike", "missile", "nuclear", "conflict",
    "ukraine", "russia", "iran", "israel", "middle east",
    "china", "taiwan", "north korea",
    "india pakistan", "escalat",
    "recession", "crash", "market sell", "risk off",
    "central bank", "gold reserve", "brics",
    "oil price", "crude", "energy crisis",
    "debt", "default", "banking crisis",
]


def _get_working_instance() -> str | None:
    for instance in NITTER_INSTANCES:
        try:
            r = requests.get(f"{instance}/twitter", timeout=6,
                             headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200:
                return instance
        except Exception:
            continue
    return None


def _is_relevant(text: str) -> bool:
    t = text.lower()
    return any(kw in t for kw in GOLD_KEYWORDS)


def _scrape_account(base_url: str, handle: str, display_name: str) -> list[dict]:
    tweets = []
    try:
        url = f"{base_url}/{handle}"
        r = requests.get(url, timeout=10,
                         headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        if r.status_code != 200:
            return []

        soup = BeautifulSoup(r.text, "html.parser")
        tweet_items = soup.select(".timeline-item")

        for item in tweet_items[:10]:
            # Get tweet text
            content_el = item.select_one(".tweet-content")
            if not content_el:
                continue
            text = content_el.get_text(strip=True)

            # Get tweet link
            link_el = item.select_one(".tweet-link")
            if not link_el:
                continue
            tweet_path = link_el.get("href", "")
            tweet_url = f"https://twitter.com{tweet_path}"

            # Keyword filter before AI
            if not _is_relevant(text):
                continue

            tweets.append({
                "title": f"@{handle}: {text[:200]}",
                "description": text[:500],
                "url": tweet_url,
                "source": f"Twitter — @{handle} ({display_name})",
                "source_type": "twitter",
                "published": datetime.utcnow().isoformat(),
            })

    except Exception as e:
        print(f"[Twitter] Error scraping @{handle}: {e}")

    return tweets


def fetch_twitter_news() -> list[dict]:
    instance = _get_working_instance()
    if not instance:
        print("[Twitter] No Nitter instances available right now — skipping Twitter.")
        return []

    print(f"[Twitter] Using Nitter instance: {instance}")
    all_tweets = []

    for handle, display_name in TWITTER_ACCOUNTS:
        tweets = _scrape_account(instance, handle, display_name)
        all_tweets.extend(tweets)
        if tweets:
            print(f"[Twitter] @{handle}: {len(tweets)} relevant tweets")

    print(f"[Twitter] Total: {len(all_tweets)} relevant tweets across all accounts")
    return all_tweets
