DEFAULT_WATCHLIST = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "JPM", "V", "JNJ",
    "WMT", "PG", "UNH", "HD", "MA", "DIS", "NFLX", "PYPL", "ADBE", "CRM",
    "INTC", "AMD", "QCOM", "AVGO", "COST", "PEP", "KO", "MRK", "ABBV", "LLY",
]


def filter_candidates(
    candidates: list[dict],
    min_volume: int = 1_000_000,
    min_market_cap: float = 1e9,
    max_symbols: int = 50,
) -> list[dict]:
    """Filter stock candidates by volume and market cap."""
    filtered = [
        c for c in candidates
        if c.get("avg_volume", 0) >= min_volume
        and c.get("market_cap", 0) >= min_market_cap
    ]
    # Sort by volume descending, take top N
    filtered.sort(key=lambda c: c.get("avg_volume", 0), reverse=True)
    return filtered[:max_symbols]
