import pytest
from src.agents.risk import RiskAgent, RiskLevel


@pytest.fixture
def agent(risk_settings):
    return RiskAgent(**risk_settings)


@pytest.fixture
def basic_portfolio(sample_portfolio):
    return sample_portfolio


def test_pre_trade_passes_valid_order(agent, basic_portfolio):
    order = {"symbol": "AAPL", "side": "buy", "risk_amount": 1500, "sector": "Technology"}
    result = agent.pre_trade_check(order, basic_portfolio)
    assert result.passed is True
    assert len(result.failures) == 0


def test_pre_trade_blocks_excessive_risk(agent, basic_portfolio):
    order = {"symbol": "AAPL", "side": "buy", "risk_amount": 3000, "sector": "Technology"}
    result = agent.pre_trade_check(order, basic_portfolio)
    assert result.passed is False
    assert "max_risk_per_trade" in result.failures


def test_pre_trade_blocks_daily_loss_exceeded(agent, basic_portfolio):
    basic_portfolio["daily_pnl"] = -3100  # Already lost 3.1% of 100K (exceeds 3% limit)
    order = {"symbol": "AAPL", "side": "buy", "risk_amount": 500, "sector": "Technology"}
    result = agent.pre_trade_check(order, basic_portfolio)
    assert result.passed is False
    assert "max_daily_loss" in result.failures


def test_pre_trade_blocks_portfolio_heat(agent, basic_portfolio):
    basic_portfolio["positions"] = [
        {"symbol": "TSLA", "risk_amount": 2000, "sector": "Consumer Cyclical"},
        {"symbol": "MSFT", "risk_amount": 2000, "sector": "Technology"},
        {"symbol": "GOOGL", "risk_amount": 1500, "sector": "Communication Services"},
    ]
    order = {"symbol": "AAPL", "side": "buy", "risk_amount": 1500, "sector": "Technology"}
    result = agent.pre_trade_check(order, basic_portfolio)
    assert result.passed is False
    assert "max_portfolio_heat" in result.failures


def test_pre_trade_blocks_sector_overexposure(agent, basic_portfolio):
    basic_portfolio["positions"] = [
        {"symbol": "AAPL", "risk_amount": 1000, "sector": "Technology", "market_value": 20000},
        {"symbol": "MSFT", "risk_amount": 1000, "sector": "Technology", "market_value": 5000},
    ]
    order = {"symbol": "NVDA", "side": "buy", "risk_amount": 1000, "sector": "Technology", "market_value": 2000}
    # Total tech exposure would be 27K / 100K = 27% > 25%
    result = agent.pre_trade_check(order, basic_portfolio)
    assert result.passed is False
    assert "max_sector_exposure" in result.failures


def test_pre_trade_blocks_consecutive_losses(agent, basic_portfolio):
    basic_portfolio["consecutive_losses"] = 3
    order = {"symbol": "AAPL", "side": "buy", "risk_amount": 500, "sector": "Technology"}
    result = agent.pre_trade_check(order, basic_portfolio)
    assert result.passed is False
    assert "max_consecutive_losses" in result.failures


def test_circuit_breaker_level_none(agent, basic_portfolio):
    level = agent.get_circuit_breaker_level(basic_portfolio)
    assert level == RiskLevel.NORMAL


def test_circuit_breaker_level_1(agent, basic_portfolio):
    basic_portfolio["equity"] = 95000  # 5% drawdown from 100K peak
    level = agent.get_circuit_breaker_level(basic_portfolio)
    assert level == RiskLevel.REDUCED_50


def test_circuit_breaker_level_2(agent, basic_portfolio):
    basic_portfolio["equity"] = 92000  # 8% drawdown
    level = agent.get_circuit_breaker_level(basic_portfolio)
    assert level == RiskLevel.REDUCED_25


def test_circuit_breaker_level_3(agent, basic_portfolio):
    basic_portfolio["equity"] = 89000  # 11% drawdown
    level = agent.get_circuit_breaker_level(basic_portfolio)
    assert level == RiskLevel.STOPPED


def test_position_size_calculation(agent, basic_portfolio):
    size = agent.calculate_position_size(
        portfolio=basic_portfolio,
        entry_price=100.0,
        stop_loss_price=96.0,
    )
    # Risk = 2% of 100K = $2000, per-share risk = $4, qty = 500
    assert size == 500


def test_position_size_respects_circuit_breaker(agent, basic_portfolio):
    basic_portfolio["equity"] = 95000  # Level 1: 50% reduction
    size = agent.calculate_position_size(
        portfolio=basic_portfolio,
        entry_price=100.0,
        stop_loss_price=96.0,
    )
    # Risk = 2% of 95K = $1900, 50% reduction = $950, per-share risk = $4, qty = 237
    assert size == 237
