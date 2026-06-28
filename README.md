# Gold Intel Bot v2 — Setup Guide

## Local Setup (PC)

1. Install new dependency:
```
pip install -r requirements.txt
```

2. Open bot.py and paste your keys at the top:
```python
DISCORD_TOKEN = "your_token"
CHANNEL_ID    = 1520809434744487966
GROQ_API_KEY  = "your_groq_key"
```

3. Run:
```
python bot.py
```

---

## 24/7 Hosting on Railway (Free)

### Step 1 — GitHub
- Go to github.com → sign up
- New Repository → name: `gold-bot` → Public → Create
- Upload all files from this folder to the repo (drag and drop on GitHub website)

### Step 2 — Railway
- Go to railway.app → Sign up with GitHub
- Click **New Project** → **Deploy from GitHub repo**
- Select your `gold-bot` repo
- Go to **Variables** tab → add:
  ```
  DISCORD_TOKEN     = your_discord_token
  DISCORD_CHANNEL_ID = 1520809434744487966
  GROQ_API_KEY      = your_groq_key
  ```
- Railway auto-detects the Procfile and deploys
- Bot runs 24/7 even when your PC is off ✅
- Free tier = 500 hours/month (enough for always-on)

---

## Commands

| Command | What it does |
|---|---|
| `!check` | Manually scan right now |
| `!status` | Show bot info |
| `!sources` | List all news sources |

---

## What's New in v2

- ✅ Twitter scraping via Nitter (no API key)
- ✅ Monitors: Trump, Fed, Kitco, ZeroHedge, Unusual Whales, Axios, Reuters
- ✅ War/geopolitical keywords: Ukraine, Russia, Israel, Iran, India-Pakistan, Taiwan
- ✅ Oil price monitoring (correlates with gold)
- ✅ Banking crisis detection
- ✅ BBC World + Al Jazeera + Middle East Eye added
- ✅ Checks every 15 minutes (was 20)
- ✅ Railway 24/7 hosting support
