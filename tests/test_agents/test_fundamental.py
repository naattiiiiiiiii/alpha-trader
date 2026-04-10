from src.agents.fundamental import FundamentalAgent, _compute_fundamental_score


def test_compute_score_strong_company():
    """A company with good fundamentals should score positive."""
    metrics = {
        "pe_ratio": 15.0,
        "pb_ratio": 2.0,
        "peg_ratio": 1.0,
        "roe": 0.20,
        "roa": 0.10,
        "net_margin": 0.15,
        "debt_to_equity": 0.5,
        "current_ratio": 2.0,
        "free_cash_flow": 5_000_000_000,
        "revenue_growth": 0.15,
        "eps_growth": 0.20,
        "sector_pe_avg": 20.0,
    }
    score = _compute_fundamental_score(metrics)
    assert score > 20  # Should be clearly positive


def test_compute_score_weak_company():
    """A company with poor fundamentals should score negative."""
    metrics = {
        "pe_ratio": 80.0,
        "pb_ratio": 10.0,
        "peg_ratio": 4.0,
        "roe": 0.02,
        "roa": 0.01,
        "net_margin": 0.01,
        "debt_to_equity": 3.0,
        "current_ratio": 0.5,
        "free_cash_flow": -1_000_000_000,
        "revenue_growth": -0.10,
        "eps_growth": -0.15,
        "sector_pe_avg": 20.0,
    }
    score = _compute_fundamental_score(metrics)
    assert score < -20  # Should be clearly negative


def test_compute_score_in_range():
    metrics = {
        "pe_ratio": 25.0,
        "pb_ratio": 3.0,
        "peg_ratio": 2.0,
        "roe": 0.10,
        "roa": 0.05,
        "net_margin": 0.08,
        "debt_to_equity": 1.0,
        "current_ratio": 1.5,
        "free_cash_flow": 1_000_000_000,
        "revenue_growth": 0.05,
        "eps_growth": 0.05,
        "sector_pe_avg": 22.0,
    }
    score = _compute_fundamental_score(metrics)
    assert -100 <= score <= 100


def test_compute_score_missing_data():
    """None values should not crash scoring."""
    metrics = {
        "pe_ratio": None,
        "pb_ratio": None,
        "peg_ratio": None,
        "roe": None,
        "roa": None,
        "net_margin": None,
        "debt_to_equity": None,
        "current_ratio": None,
        "free_cash_flow": None,
        "revenue_growth": None,
        "eps_growth": None,
        "sector_pe_avg": None,
    }
    score = _compute_fundamental_score(metrics)
    assert score == 0  # Neutral when no data
