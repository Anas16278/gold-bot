import os
import json
import requests

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.1-8b-instant"

SYSTEM_PROMPT = """You are a professional gold (XAU/USD) market analyst. Your job is to read news and tweets and decide if they will significantly move the Gold price.

Respond ONLY with valid JSON. No markdown, no preamble, nothing outside the JSON.

JSON format:
{
  "relevant": true or false,
  "bias": "bullish" or "bearish" or "neutral",
  "impact": "high" or "medium",
  "summary": "One plain English sentence summarising the news",
  "reason": "One sentence explaining WHY this moves gold and in which direction"
}

Gold goes BULLISH (price rises) when:
- Active wars escalate or new conflicts break out (Ukraine, Middle East, India-Pakistan, Taiwan)
- Airstrikes, missile attacks, invasions announced
- Geopolitical tensions rise significantly
- Trump announces tariffs, trade wars, sanctions, or economic chaos
- Fed signals rate cuts or dovish policy
- US dollar weakens (DXY falling)
- Inflation data beats expectations (hot CPI/PCE)
- Banking crises, market crashes, risk-off environment
- Central banks increase gold reserves
- BRICS de-dollarisation news
- Oil price spikes (energy crisis)
- US debt ceiling crisis

Gold goes BEARISH (price falls) when:
- Wars de-escalate, ceasefires announced
- Fed signals rate hikes or hawkish stance
- US dollar strengthens significantly
- Inflation cools below expectations
- Strong economic data (GDP beats, low unemployment)
- Risk-on environment (stocks rallying)

Set relevant=false for:
- Routine political statements with no market impact
- Sports, entertainment, celebrity news
- Minor local news
- Company earnings (unless major bank collapse)
- Old news being recycled

Only flag HIGH impact for things that will genuinely move gold 0.5%+ in a session."""


def analyse_article(article: dict) -> dict | None:
    if not GROQ_API_KEY:
        print("[AI] No GROQ_API_KEY!")
        return None

    headline = article.get("title", "")
    description = article.get("description", "")[:400]
    source = article.get("source", "")
    source_type = article.get("source_type", "rss")

    prompt = f"""{"Tweet" if source_type == "twitter" else "News article"} from {source}:

Headline/Text: {headline}
Details: {description}

Is this high-impact for Gold (XAU/USD)? JSON only."""

    try:
        response = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": 300,
                "temperature": 0.1,
            },
            timeout=15,
        )

        data = response.json()
        if "error" in data:
            print(f"[Groq Error] {data['error']}")
            return None

        raw = data["choices"][0]["message"]["content"].strip()

        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        result = json.loads(raw)
        status = f"relevant={result.get('relevant')}, bias={result.get('bias')}"
        print(f"[AI] '{headline[:55]}...' → {status}")
        return result

    except json.JSONDecodeError as e:
        print(f"[AI] JSON parse error: {e}")
        return None
    except Exception as e:
        print(f"[AI] Error: {e}")
        return None
