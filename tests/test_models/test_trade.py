from src.models.trade import Trade
from sqlalchemy import inspect


def test_trade_table_name():
    assert Trade.__tablename__ == "trades"


def test_trade_columns():
    columns = {c.name for c in inspect(Trade).columns}
    expected = {
        "id", "symbol", "side", "qty", "entry_price", "exit_price",
        "entry_time", "exit_time", "status", "stop_loss", "take_profit",
        "pnl", "pnl_pct", "alpaca_order_id", "time_horizon",
    }
    assert expected.issubset(columns)
