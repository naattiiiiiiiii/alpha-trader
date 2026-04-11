import pytest
from src.core.portfolio import PortfolioManager


def test_initial_state():
    pm = PortfolioManager(initial_equity=100_000)
    state = pm.get_state()
    assert state["equity"] == 100_000
    assert state["peak_equity"] == 100_000
    assert state["daily_pnl"] == 0
    assert state["consecutive_losses"] == 0
    assert len(state["positions"]) == 0


def test_update_from_alpaca():
    pm = PortfolioManager(initial_equity=100_000)
    pm.update_from_account(equity=102_000, cash=70_000, buying_power=70_000)
    state = pm.get_state()
    assert state["equity"] == 102_000
    assert state["peak_equity"] == 102_000  # New peak


def test_peak_tracks_highest():
    pm = PortfolioManager(initial_equity=100_000)
    pm.update_from_account(equity=105_000, cash=70_000, buying_power=70_000)
    pm.update_from_account(equity=103_000, cash=72_000, buying_power=72_000)
    state = pm.get_state()
    assert state["peak_equity"] == 105_000  # Still the old peak


def test_drawdown_calculation():
    pm = PortfolioManager(initial_equity=100_000)
    pm.update_from_account(equity=105_000, cash=70_000, buying_power=70_000)
    pm.update_from_account(equity=94_500, cash=80_000, buying_power=80_000)
    assert pm.get_drawdown_pct() == pytest.approx(0.10, abs=0.001)


def test_portfolio_heat():
    pm = PortfolioManager(initial_equity=100_000)
    pm.update_positions([
        {"symbol": "AAPL", "risk_amount": 1500, "sector": "Technology", "market_value": 10000},
        {"symbol": "TSLA", "risk_amount": 1000, "sector": "Consumer Cyclical", "market_value": 8000},
    ])
    assert pm.get_portfolio_heat() == pytest.approx(0.025, abs=0.001)


def test_record_trade_result_win():
    pm = PortfolioManager(initial_equity=100_000)
    pm.record_trade_result(pnl=500)
    assert pm._consecutive_losses == 0
    assert pm._daily_pnl == 500


def test_record_trade_result_loss():
    pm = PortfolioManager(initial_equity=100_000)
    pm.record_trade_result(pnl=-200)
    pm.record_trade_result(pnl=-300)
    assert pm._consecutive_losses == 2
    assert pm._daily_pnl == -500


def test_reset_daily():
    pm = PortfolioManager(initial_equity=100_000)
    pm.record_trade_result(pnl=-500)
    pm.reset_daily()
    assert pm._daily_pnl == 0
    # Consecutive losses persist across days
    assert pm._consecutive_losses == 1
