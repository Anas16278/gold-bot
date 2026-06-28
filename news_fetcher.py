import feedparser
import requests
from datetime import datetime, timedelta

RSS_FEEDS = [
    ("Kitco News",          "https://www.kitco.com/rss/kitconews.xml"),
    ("Mining.com",          "https://www.mining.com/feed/"),
    ("Reuters Business",    "https://feeds.reuters.com/reuters/businessNews"),
    ("Reuters US News",     "https://feeds.reuters.com/reuters/USnews"),
    ("MarketWatch Top",     "https://feeds.marketwatch.com/marketwatch/topstories"),
    ("BBC Business",        "https://feeds.bbci.co.uk/news/business/rss.xml"),
    ("BBC World",           "https://feeds.bbci.co.uk/news/world/rss.xml"),
    ("FT Markets",          "https://www.ft.com/rss/home/uk"),
    ("Bloomberg Markets",   "https://feeds.bloomberg.com/markets/news.rss"),
    ("CNBC Economy",        "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=20910258"),
    ("CNBC World",          "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100727362"),
    ("Investing.com Gold",  "https://www.investing.com/rss/news_301.rss"),
    ("Investing.com Macro", "https://www.investing.com/rss/news_14.rss"),
    ("Al Jazeera",          "https://www.aljazeera.com/xml/rss/all.xml"),
    ("Middle East Eye",     "https://www.middleeasteye.net/rss"),
]

GOLD_KEYWORDS = [
    # Direct gold
    "gold", "xau", "bullion", "precious metal", "safe haven",

    # Trump / US politics (huge gold mover)
    "trump", "tariff", "trade war", "trade deal", "trade deficit",
    "sanction", "embargo", "executive order", "white house",

    # Fed / interest rates
    "federal reserve", "fed rate", "powell", "fomc",
    "rate cut", "rate hike", "interest rate", "monetary policy",
    "quantitative easing", "quantitative tightening", "balance sheet",

    # Inflation / macro data
    "cpi", "inflation", "pce", "nonfarm", "nfp", "jobs report",
    "unemployment", "gdp", "recession", "stagflation",
    "debt ceiling", "us debt", "fiscal",

    # Dollar
    "dollar", "dxy", "dollar index", "usd",
    "de-dollarisation", "dedollar", "dollar dominance",

    # Active wars & conflicts (2025-2026)
    "ukraine", "russia", "zelensky", "putin", "nato",
    "israel", "gaza", "hamas", "hezbollah", "iran",
    "middle east", "airstrike", "missile strike",
    "india pakistan", "kashmir", "pakistan",
    "china taiwan", "taiwan strait", "south china sea",
    "north korea", "kim jong",
    "red sea", "houthi", "shipping lane",
    "nuclear", "wmd", "weapon of mass",

    # Geopolitical general
    "war", "conflict", "invasion", "ceasefire", "escalat",
    "coup", "regime", "crisis", "emergency",
    "refugee", "evacuate",

    # Energy (oil correlates with gold)
    "oil price", "crude oil", "opec", "energy crisis",
    "pipeline", "lng", "natural gas",

    # Banking / financial crisis
    "bank collapse", "banking crisis", "credit crisis",
    "default", "sovereign debt", "bailout",
    "market crash", "stock crash", "circuit breaker",

    # Central banks
    "central bank", "imf", "world bank", "gold reserve",
    "brics", "reserve currency",
]


def _is_relevant(text: str) -> bool:
    t = text.lower()
    return any(kw in t for kw in GOLD_KEYWORDS)


def fetch_gold_news() -> list[dict]:
    articles = []
    seen_urls = set()

    for source_name, feed_url in RSS_FEEDS:
        try:
            headers = {"User-Agent": "Mozilla/5.0 (compatible; GoldBot/2.0)"}
            raw = requests.get(feed_url, headers=headers, timeout=10)
            feed = feedparser.parse(raw.content)

            for entry in feed.entries[:20]:
                title = entry.get("title", "").strip()
                summary = entry.get("summary", "") or entry.get("description", "")
                url = entry.get("link", "").strip()

                if not title or not url or url in seen_urls:
                    continue

                if not _is_relevant(title + " " + summary):
                    continue

                seen_urls.add(url)
                articles.append({
                    "title": title,
                    "description": summary[:600],
                    "url": url,
                    "source": source_name,
                    "source_type": "rss",
                    "published": entry.get("published", ""),
                })

        except Exception as e:
            print(f"[RSS Error] {source_name}: {e}")

    print(f"[RSS] {len(articles)} keyword-matched articles from {len(RSS_FEEDS)} feeds.")
    return articles
