from datetime import datetime
from src.core.maintenance import (
    get_cleanup_cutoff,
    should_alert_no_cycles,
    HealthStatus,
)


def test_cleanup_cutoff_snapshots():
    cutoff = get_cleanup_cutoff("snapshots", now=datetime(2026, 4, 10))
    expected = datetime(2026, 1, 10)  # 90 days ago
    assert cutoff == expected


def test_cleanup_cutoff_logs():
    cutoff = get_cleanup_cutoff("logs", now=datetime(2026, 4, 10))
    expected = datetime(2026, 3, 11)  # 30 days ago
    assert cutoff == expected


def test_cleanup_cutoff_signals():
    cutoff = get_cleanup_cutoff("signals", now=datetime(2026, 4, 10))
    expected = datetime(2025, 10, 12)  # 180 days ago
    assert cutoff == expected


def test_should_alert_no_cycles_during_market():
    # Market hours, no cycle in 35 minutes -> alert
    last_cycle = datetime(2026, 4, 10, 10, 0)  # 10:00 ET
    now = datetime(2026, 4, 10, 10, 35)  # 10:35 ET
    assert should_alert_no_cycles(last_cycle, now, market_open=True) is True


def test_should_not_alert_recent_cycle():
    last_cycle = datetime(2026, 4, 10, 10, 0)
    now = datetime(2026, 4, 10, 10, 20)  # 20 min later
    assert should_alert_no_cycles(last_cycle, now, market_open=True) is False


def test_should_not_alert_outside_market():
    last_cycle = datetime(2026, 4, 10, 10, 0)
    now = datetime(2026, 4, 10, 18, 0)  # After hours
    assert should_alert_no_cycles(last_cycle, now, market_open=False) is False


def test_health_status_all_ok():
    status = HealthStatus(alpaca=True, claude=True, database=True, telegram=True)
    assert status.is_healthy is True


def test_health_status_degraded():
    status = HealthStatus(alpaca=True, claude=False, database=True, telegram=True)
    assert status.is_healthy is False
    assert "claude" in status.failed_components
