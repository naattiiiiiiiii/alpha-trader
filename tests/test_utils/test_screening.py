from src.utils.screening import filter_candidates, DEFAULT_WATCHLIST


def test_default_watchlist_not_empty():
    assert len(DEFAULT_WATCHLIST) >= 20


def test_filter_candidates_by_volume():
    candidates = [
        {"symbol": "AAPL", "avg_volume": 50_000_000, "market_cap": 3e12},
        {"symbol": "TINY", "avg_volume": 100_000, "market_cap": 500e6},  # Below 1M volume
        {"symbol": "MSFT", "avg_volume": 30_000_000, "market_cap": 2.5e12},
    ]
    result = filter_candidates(candidates, min_volume=1_000_000, min_market_cap=1e9)
    symbols = [c["symbol"] for c in result]
    assert "AAPL" in symbols
    assert "MSFT" in symbols
    assert "TINY" not in symbols


def test_filter_candidates_by_market_cap():
    candidates = [
        {"symbol": "AAPL", "avg_volume": 50_000_000, "market_cap": 3e12},
        {"symbol": "SMALL", "avg_volume": 5_000_000, "market_cap": 500e6},  # Below 1B cap
    ]
    result = filter_candidates(candidates, min_volume=1_000_000, min_market_cap=1e9)
    symbols = [c["symbol"] for c in result]
    assert "AAPL" in symbols
    assert "SMALL" not in symbols


def test_filter_respects_max_size():
    candidates = [
        {"symbol": f"SYM{i}", "avg_volume": 10_000_000, "market_cap": 5e9}
        for i in range(100)
    ]
    result = filter_candidates(candidates, max_symbols=50)
    assert len(result) == 50
