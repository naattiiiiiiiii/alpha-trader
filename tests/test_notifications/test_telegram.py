from src.notifications.telegram import format_trade_message, format_daily_summary


def test_format_trade_buy():
    msg = format_trade_message(
        action="BUY", symbol="AAPL", qty=10, price=178.50,
        stop_loss=174.90, take_profit=185.20, reasoning="Strong confluence"
    )
    assert "BUY" in msg
    assert "AAPL" in msg
    assert "178.50" in msg
    assert "Strong confluence" in msg


def test_format_trade_stop_loss():
    msg = format_trade_message(
        action="STOP-LOSS", symbol="AAPL", qty=10, price=174.90,
        pnl=-36.0, pnl_pct=-2.0
    )
    assert "STOP-LOSS" in msg
    assert "-$36.00" in msg or "-36.00" in msg


def test_format_daily_summary():
    msg = format_daily_summary(
        trades_count=3, wins=2, losses=1,
        daily_pnl=85.30, equity=100_085.30,
        drawdown_pct=0.0,
    )
    assert "3" in msg
    assert "2" in msg
    assert "85.30" in msg
