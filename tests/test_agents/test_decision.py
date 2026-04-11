import pytest
from src.agents.decision import _build_decision_prompt, _parse_decision, DecisionOutput


def test_build_prompt_includes_all_scores():
    prompt = _build_decision_prompt(
        symbol="AAPL",
        technical_score=72,
        fundamental_score=45,
        sentiment_score=85,
        portfolio_state={"equity": 100000, "positions": [], "cash": 80000},
        risk_budget_pct=1.8,
    )
    assert "AAPL" in prompt
    assert "72" in prompt
    assert "45" in prompt
    assert "85" in prompt
    assert "1.8" in prompt


def test_parse_decision_valid():
    response = '''{
        "action": "BUY",
        "symbol": "AAPL",
        "position_size_pct": 1.5,
        "entry_strategy": "limit",
        "take_profit_pct": 4.0,
        "stop_loss_pct": 2.0,
        "reasoning": "Strong confluence",
        "time_horizon": "swing",
        "confidence": 0.82
    }'''
    result = _parse_decision(response)
    assert result.action == "BUY"
    assert result.symbol == "AAPL"
    assert result.confidence == 0.82
    assert result.stop_loss_pct == 2.0


def test_parse_decision_hold():
    response = '''{
        "action": "HOLD",
        "symbol": "AAPL",
        "position_size_pct": 0,
        "entry_strategy": "none",
        "take_profit_pct": 0,
        "stop_loss_pct": 0,
        "reasoning": "Mixed signals",
        "time_horizon": "none",
        "confidence": 0.3
    }'''
    result = _parse_decision(response)
    assert result.action == "HOLD"


def test_parse_decision_invalid_json():
    result = _parse_decision("garbage")
    assert result.action == "HOLD"
    assert result.confidence == 0.0


def test_should_invoke_decisor_true():
    from src.agents.decision import should_invoke_decisor
    assert should_invoke_decisor(technical=65, fundamental=50, sentiment=10, threshold=40) is True


def test_should_invoke_decisor_false():
    from src.agents.decision import should_invoke_decisor
    assert should_invoke_decisor(technical=10, fundamental=20, sentiment=10, threshold=40) is False
