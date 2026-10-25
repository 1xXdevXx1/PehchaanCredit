import pytest
import pandas as pd
from backend.ml.scoring import compute_final_credit_score, compute_behavioral_trust_score
from backend.ml.decision_engine import make_lender_decision

def test_end_to_end_single_vendor():
    # Emulate complete flow for healthy vendor
    spv = 0.85
    tsci = 0.88
    mcs = 0.82
    resilience = 0.95
    svps = 0.05
    q_base = 0.82

    score_info = compute_final_credit_score(q_base, svps)
    trust = compute_behavioral_trust_score(spv, tsci, mcs, resilience, svps)
    dec = make_lender_decision(score_info['credit_score'], svps, score_info['rating'], [])

    assert score_info['credit_score'] >= 750
    assert score_info['rating'] in ['Very Good', 'Excellent']
    assert trust >= 80
    assert dec['decision'] == 'STRONG_APPROVAL';