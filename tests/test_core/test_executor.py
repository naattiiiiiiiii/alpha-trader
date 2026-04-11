import pytest
from src.core.executor import OrderRequest


def test_order_request_bracket_prices():
    req = OrderRequest(
        symbol="AAPL",
        side="buy",
        qty=10,
        entry_price=100.0,
        stop_loss_pct=2.0,
        take_profit_pct=4.0,
    )
    assert req.stop_loss_price == 98.0
    assert req.take_profit_price == 104.0


def test_order_request_sell_bracket_prices():
    req = OrderRequest(
        symbol="AAPL",
        side="sell",
        qty=10,
        entry_price=100.0,
        stop_loss_pct=2.0,
        take_profit_pct=4.0,
    )
    # For short: stop is above, take profit is below
    assert req.stop_loss_price == 102.0
    assert req.take_profit_price == 96.0


def test_order_request_validates_qty():
    with pytest.raises(ValueError, match="qty must be positive"):
        OrderRequest(symbol="AAPL", side="buy", qty=0, entry_price=100.0,
                     stop_loss_pct=2.0, take_profit_pct=4.0)


def test_order_request_validates_rr_ratio():
    with pytest.raises(ValueError, match="risk/reward"):
        OrderRequest(symbol="AAPL", side="buy", qty=10, entry_price=100.0,
                     stop_loss_pct=5.0, take_profit_pct=2.0, min_rr_ratio=2.0)
