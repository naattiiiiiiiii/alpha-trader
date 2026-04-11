import json
import hashlib
import logging
from openai import AsyncOpenAI

from src.agents.base import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


def _build_prompt(symbol: str, news_items: list[str]) -> str:
    news_text = "\n".join(f"- {item}" for item in news_items) if news_items else "No recent news."
    return f"""Analyze the following news/events for stock {symbol} and assess their likely impact on the stock price in the short term (1-5 days).

Recent news:
{news_text}

Respond with ONLY a JSON object (no markdown, no explanation):
{{"score": <integer -100 to 100>, "summary": "<one line summary>", "urgency": "<low|medium|high>"}}

Score guide:
- +80 to +100: Extremely positive (major beat, FDA approval, huge contract)
- +40 to +79: Positive (good earnings, upgrade, positive guidance)
- -39 to +39: Neutral or mixed
- -79 to -40: Negative (miss, downgrade, lawsuit)
- -100 to -80: Extremely negative (fraud, bankruptcy risk, major recall)"""


def _parse_response(text: str) -> dict:
    try:
        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        data = json.loads(text)
        score = max(-100, min(100, int(data.get("score", 0))))
        return {
            "score": score,
            "summary": data.get("summary", ""),
            "urgency": data.get("urgency", "low"),
        }
    except (json.JSONDecodeError, ValueError, KeyError):
        return {"score": 0, "summary": "Failed to parse LLM response", "urgency": "low"}


class SentimentAgent(BaseAgent):
    name = "sentiment"

    def __init__(
        self,
        base_url: str = "http://localhost:11434/v1",
        api_key: str = "ollama",
        model: str = "llama3.2",
        alpaca_api_key: str = "",
        alpaca_secret_key: str = "",
    ):
        self._client = AsyncOpenAI(base_url=base_url, api_key=api_key)
        self._model = model
        self._cache: dict[str, dict] = {}
        self._alpaca_api_key = alpaca_api_key
        self._alpaca_secret_key = alpaca_secret_key
        self._news_client = None
        if alpaca_api_key and alpaca_secret_key:
            from alpaca.data.historical.news import NewsClient
            self._news_client = NewsClient(
                api_key=alpaca_api_key, secret_key=alpaca_secret_key,
            )

    def _compute_news_hash(self, news_items: list[str]) -> str:
        content = "|".join(sorted(news_items))
        return hashlib.md5(content.encode()).hexdigest()

    async def _fetch_news(self, symbol: str) -> list[str]:
        """Fetch latest news headlines from Alpaca for the given symbol."""
        if self._news_client is None:
            return []
        try:
            from alpaca.data.requests import NewsRequest
            request = NewsRequest(symbols=symbol, limit=10)
            response = self._news_client.get_news(request)
            news_list = response.data.get("news", [])
            headlines = [item.headline for item in news_list if item.headline]
            logger.info(f"{symbol}: fetched {len(headlines)} news headlines from Alpaca")
            return headlines
        except Exception as e:
            logger.error(f"Failed to fetch news for {symbol}: {e}")
            return []

    async def analyze(self, symbol: str) -> AgentResult:
        news_items = await self._fetch_news(symbol)
        news_hash = self._compute_news_hash(news_items)

        # Check cache
        cached = self._cache.get(symbol)
        if cached and cached.get("news_hash") == news_hash:
            return AgentResult(
                score=cached["score"],
                indicators={"cached": True, "urgency": cached.get("urgency", "low")},
                reasoning=f"cached: {cached['summary']}",
            )

        if not news_items:
            return AgentResult(score=0, reasoning="No news available")

        prompt = _build_prompt(symbol, news_items)
        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.1,
            )
            parsed = _parse_response(response.choices[0].message.content)
        except Exception as e:
            return AgentResult(score=0, reasoning=f"LLM error: {e}")

        # Update cache
        self._cache[symbol] = {**parsed, "news_hash": news_hash}

        return AgentResult(
            score=parsed["score"],
            indicators={"urgency": parsed["urgency"], "cached": False},
            reasoning=parsed["summary"],
        )
