import discord
from discord.ext import commands, tasks
import asyncio
import os
from datetime import datetime

# ── Keys: works both locally (hardcoded) and on Railway (env vars) ────────────
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
CHANNEL_ID    = int(os.environ.get("DISCORD_CHANNEL_ID", "1520809434744487966"))
GROQ_API_KEY  = os.environ.get("GROQ_API_KEY")
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

# Make Groq key available to ai_filter.py
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

from news_fetcher import fetch_gold_news
from twitter_scraper import fetch_twitter_news
from ai_filter import analyse_article
from seen_tracker import has_seen, mark_seen

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


def build_embed(article: dict, analysis: dict) -> discord.Embed:
    bias = analysis.get("bias", "neutral").lower()
    is_twitter = article.get("source_type") == "twitter"

    if bias == "bullish":
        colour = 0x00C853
        emoji = "📈"
        bias_label = "📈 BULLISH for Gold"
    elif bias == "bearish":
        colour = 0xFF1744
        emoji = "📉"
        bias_label = "📉 BEARISH for Gold"
    else:
        colour = 0xFFAB00
        emoji = "⚠️"
        bias_label = "⚠️ NEUTRAL / WATCH"

    source_icon = "🐦" if is_twitter else "📰"
    title_prefix = f"{emoji} {'TWEET ALERT' if is_twitter else 'GOLD ALERT'}"

    embed = discord.Embed(
        title=f"{title_prefix}  —  {article['title'][:200]}",
        url=article.get("url", ""),
        colour=colour,
        timestamp=datetime.utcnow()
    )

    embed.add_field(name="📋 Summary", value=analysis.get("summary", "No summary."), inline=False)
    embed.add_field(name="📊 Market Bias", value=bias_label, inline=True)
    embed.add_field(name="🔥 Impact", value=analysis.get("impact", "HIGH").upper(), inline=True)
    embed.add_field(name="💡 Why This Moves Gold", value=analysis.get("reason", "N/A"), inline=False)
    embed.add_field(name=f"{source_icon} Source", value=f"[{'View Tweet' if is_twitter else 'Read Article'}]({article.get('url', '')})", inline=False)
    embed.set_footer(text=f"📡 {article.get('source', 'Unknown')}  •  Gold Intel Bot v2")

    return embed


@tasks.loop(minutes=15)
async def check_news():
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print(f"[ERROR] Cannot find channel {CHANNEL_ID}")
        return

    print(f"[{datetime.utcnow().strftime('%H:%M:%S')} UTC] Scanning RSS + Twitter...")

    # Fetch from both sources
    rss_articles = fetch_gold_news()
    twitter_articles = fetch_twitter_news()
    all_articles = rss_articles + twitter_articles

    print(f"[Fetch] {len(rss_articles)} RSS + {len(twitter_articles)} tweets = {len(all_articles)} total candidates")

    posted = 0
    for article in all_articles:
        url = article.get("url", "")
        if not url or has_seen(url):
            continue

        analysis = analyse_article(article)

        if not analysis or analysis.get("relevant") is False:
            mark_seen(url)
            continue

        embed = build_embed(article, analysis)
        await channel.send(embed=embed)
        mark_seen(url)
        posted += 1
        await asyncio.sleep(2)

    print(f"[{datetime.utcnow().strftime('%H:%M:%S')} UTC] Posted {posted} alerts.")


@bot.event
async def on_ready():
    print(f"✅ Gold Intel Bot v2 online — {bot.user}")
    print(f"📡 Channel: {CHANNEL_ID}")
    print(f"🐦 Twitter: Monitoring via Nitter")
    check_news.start()


@bot.command(name="check")
async def manual_check(ctx):
    await ctx.send("🔍 Scanning RSS + Twitter now...")
    await check_news()


@bot.command(name="status")
async def status(ctx):
    await ctx.send(
        "✅ **Gold Intel Bot v2 — Online**\n"
        "⏱️ Scanning every **15 minutes**\n"
        "📰 RSS: Reuters · Kitco · MarketWatch · FT · BBC · Bloomberg · CNBC\n"
        "🐦 Twitter: Trump · Fed · KitcoNews · ZeroHedge · UnusualWhales\n"
        "🤖 AI: Groq Llama 3 (free)\n"
        f"📬 <#{CHANNEL_ID}>"
    )


@bot.command(name="sources")
async def sources(ctx):
    await ctx.send(
        "**📡 Active News Sources:**\n\n"
        "**RSS Feeds:**\n"
        "• Kitco News (gold-specific)\n"
        "• Mining.com\n"
        "• Reuters Business & US\n"
        "• MarketWatch\n"
        "• BBC Business\n"
        "• Financial Times\n"
        "• Bloomberg Markets\n"
        "• CNBC Economy & World\n"
        "• Investing.com Gold & Macro\n\n"
        "**Twitter (via Nitter):**\n"
        "• @realDonaldTrump\n"
        "• @federalreserve\n"
        "• @KitcoNewsNOW\n"
        "• @zerohedge\n"
        "• @unusual_whales\n"
        "• @axios (breaking geopolitical)\n"
    )


bot.run(DISCORD_TOKEN)
