import pytest
from unittest.mock import AsyncMock, patch
from src.agents.sentiment import SentimentAgent, _build_prompt, _parse_response


def test_build_prompt():
    prompt = _build_prompt("AAPL", ["Apple beats Q1 earnings expectations"])
    assert "AAPL" in prompt
    assert "Apple beats" in prompt


def test_parse_response_valid():
    response = '{"score": 75, "summary": "Strong earnings beat", "urgency": "high"}'
    result = _parse_response(response)
    assert result["score"] == 75
    assert result["summary"] == "Strong earnings beat"


def test_parse_response_invalid_json():
    result = _parse_response("not json at all")
    assert result["score"] == 0
    assert "parse" in result["summary"].lower() or "error" in result["summary"].lower()


def test_parse_response_score_clamped():
    response = '{"score": 200, "summary": "test", "urgency": "low"}'
    result = _parse_response(response)
    assert result["score"] == 100  # Clamped to max


@pytest.mark.asyncio
async def test_sentiment_agent_uses_cache():
    agent = SentimentAgent(api_key="fake")
    agent._cache["AAPL"] = {
        "score": 50,
        "summary": "cached",
        "urgency": "low",
        "news_hash": "abc123",
    }
    # Same news hash should return cached result
    with patch.object(agent, "_fetch_news", return_value=[]):
        with patch.object(agent, "_compute_news_hash", return_value="abc123"):
            result = await agent.analyze("AAPL")
    assert result.score == 50
    assert "cached" in result.reasoning
