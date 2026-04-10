import pytest


@pytest.fixture
def risk_settings():
    return {
        "max_risk_per_trade": 0.02,
        "max_daily_loss": 0.03,
        "max_portfolio_heat": 0.06,
        "max_drawdown": 0.10,
        "max_sector_exposure": 0.25,
        "max_consecutive_losses": 3,
        "min_rr_ratio": 2.0,
    }


@pytest.fixture
def sample_portfolio():
    return {
        "equity": 100_000.0,
        "cash": 80_000.0,
        "buying_power": 80_000.0,
        "peak_equity": 100_000.0,
        "daily_pnl": 0.0,
        "positions": [],
        "consecutive_losses": 0,
    }
