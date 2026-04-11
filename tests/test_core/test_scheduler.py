from src.core.scheduler import _aggregate_should_trade


def test_aggregate_should_trade_strong_signals():
    result = _aggregate_should_trade(
        technical=72, fundamental=45, sentiment=85, threshold=40
    )
    assert result is True  # 3/3 above threshold


def test_aggregate_should_trade_two_signals():
    result = _aggregate_should_trade(
        technical=65, fundamental=50, sentiment=10, threshold=40
    )
    assert result is True  # 2/3 above threshold


def test_aggregate_should_trade_weak_signals():
    result = _aggregate_should_trade(
        technical=20, fundamental=15, sentiment=10, threshold=40
    )
    assert result is False  # 0/3 above threshold


def test_aggregate_should_trade_one_signal():
    result = _aggregate_should_trade(
        technical=80, fundamental=10, sentiment=5, threshold=40
    )
    assert result is False  # Only 1/3 above threshold
