import pytest
from backend.ml.scoring import compute_final_credit_score, compute_behavioral_trust_score

def test_score_boundaries():
    # Minimum boundary
    min_res = compute_final_credit_score(q_base=0.0, svps=0.0)
    assert min_res['credit_score'] == 300
    assert min_res['rating'] == 'Poor';

    # Maximum boundary
    max_res = compute_final_credit_score(q_base=1.0, svps=0.0)
    assert max_res['credit_score'] == 900
    assert max_res['rating'] == 'Excellent';

def test_score_exact_formula():
    # Q_base = 0.78, SVPS = 0.10
    # Q_final = 0.78 * (1 - 0.25 * 0.10) = 0.78 * 0.975 = 0.7605
    # Score = 300 + 600 * 0.7605 = 300 + 456.3 = 756.3 -> 756
    res = compute_final_credit_score(q_base=0.78, svps=0.10)
    assert res['q_final'] == 0.7605
    assert res['credit_score'] == 756
    assert res['rating'] == 'Very Good';

def test_behavioral_trust_score():
    trust = compute_behavioral_trust_score(spv=0.86, tsci=0.89, mcs=0.83, resilience=0.96, svps=0.04)
    assert 10 <= trust <= 99
    assert trust >= 80