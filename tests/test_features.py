import pytest
import pandas as pd
from backend.ml.behavioral_metrics import compute_legacy_indices, compute_framework_metrics

def test_framework_metrics():
    df = pd.DataFrame([
        {'timestamp': '2026-09-01 10:00:00', 'date': '2026-09-01', 'hour': 10, 'transaction_type': 'SUPPLIER_PAYMENT', 'amount': 8000, 'counterparty_id': 'S1'},
        {'timestamp': '2026-09-01 12:00:00', 'date': '2026-09-01', 'hour': 12, 'transaction_type': 'CUSTOMER_PAYMENT', 'amount': 500, 'counterparty_id': 'C1'},
        {'timestamp': '2026-09-02 15:00:00', 'date': '2026-09-02', 'hour': 15, 'transaction_type': 'CUSTOMER_PAYMENT', 'amount': 400, 'counterparty_id': 'C2'}
    ])
    res = compute_framework_metrics(df, stl_resilience=0.92)
    assert 0.0 <= res['spv'] <= 1.0
    assert 0.0 <= res['tsci'] <= 1.0
    assert 0.0 <= res['mcs'] <= 1.0
    assert res['resilience'] == 0.92