import pytest
import pandas as pd
import numpy as np
from backend.ml.behavioral_metrics import (
    compute_circular_stats, compute_shannon_entropy, compute_haversine_dispersion,
    compute_framework_metrics
)
from backend.ml.graph_analysis import build_transaction_graph, analyze_vendor_graph
from backend.ml.advanced_tgat import Time2Vec, TemporalGraphAttention, compute_tgat_node_metrics
from backend.ml.scoring import compute_final_credit_score, compute_itemized_waterfall_statement
from backend.ml.loan_agent import process_voice_intent, verify_and_confirm_application, AuditChain
from backend.ml.account_aggregator import aa_engine
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_circular_statistics():
    # Morning vendor routine: concentrated around 6 AM
    morning_hours = pd.Series([5.8, 6.0, 6.2, 6.1, 5.9, 6.0])
    res = compute_circular_stats(morning_hours)
    assert res['R'] > 0.95
    assert res['circular_variance'] < 0.05
    assert 5.5 <= res['circular_mean_hour'] <= 6.5

    # Uniformly scattered hours: low R, high circular variance
    scattered_hours = pd.Series([1, 5, 9, 13, 17, 21])
    res_scattered = compute_circular_stats(scattered_hours)
    assert res_scattered['R'] < 0.50
    assert res_scattered['circular_variance'] > 0.50

def test_shannon_entropy():
    # Highly concentrated on a single peak hour
    concentrated_hours = pd.Series([12] * 50)
    ent_res = compute_shannon_entropy(concentrated_hours)
    assert ent_res['entropy'] == 0.0
    assert ent_res['entropy_concentration'] == 1.0

    # Evenly dispersed hours
    even_hours = pd.Series(list(range(24)))
    ent_even = compute_shannon_entropy(even_hours)
    assert ent_even['entropy_concentration'] < 0.10

def test_graph_multi_attributed_and_rar():
    df = pd.DataFrame([
        {'vendor_id': 'V1', 'counterparty_id': 'V2', 'amount': 10000.0, 'timestamp': '2026-09-01 10:00:00'},
        {'vendor_id': 'V2', 'counterparty_id': 'V1', 'amount': 9500.0, 'timestamp': '2026-09-01 11:00:00'},
        {'vendor_id': 'V2', 'counterparty_id': 'V3', 'amount': 500.0, 'timestamp': '2026-09-01 12:00:00'},
    ])
    G = build_transaction_graph(df)
    assert G.has_edge('V1', 'V2')
    assert G.has_edge('V2', 'V1')
    
    # Reciprocal amount ratio should be 9500 / 10000 = 0.95
    rar = G['V1']['V2']['reciprocal_amount_ratio']
    assert 0.90 <= rar <= 1.0
    
    analysis = analyze_vendor_graph(G, 'V1')
    assert analysis['has_cycles'] == True
    assert analysis['reciprocal_count'] >= 1
    assert analysis['max_rar'] >= 0.90

def test_tgat_time2vec():
    t2v = Time2Vec(dimension=16)
    timestamps = np.array([1700000000, 1700003600, 1700007200])
    embs = t2v.transform(timestamps)
    assert embs.shape == (3, 16)
    
    df_tx = pd.DataFrame([
        {'amount': 500.0, 'hour': 10, 'timestamp': '2026-09-01 10:00:00', 'transaction_type': 'CUSTOMER_PAYMENT'},
        {'amount': 750.0, 'hour': 12, 'timestamp': '2026-09-01 12:00:00', 'transaction_type': 'CUSTOMER_PAYMENT'}
    ])
    metrics = compute_tgat_node_metrics(df_tx)
    assert 'tgat_anomaly_score' in metrics
    assert 0.0 <= metrics['tgat_anomaly_score'] <= 1.0

def test_quantile_scoring_and_waterfall():
    score_info = compute_final_credit_score(q_base=0.80, svps=0.08)
    assert 'p10_score' in score_info
    assert 'p50_score' in score_info
    assert 'p90_score' in score_info
    assert score_info['p10_score'] <= score_info['p50_score'] <= score_info['p90_score']

    waterfall = compute_itemized_waterfall_statement(
        credit_score=score_info['credit_score'],
        spv=0.85, tsci=0.82, mcs=0.80, resilience=0.92, svps=0.08
    )
    assert waterfall['final_score'] == score_info['credit_score']
    assert len(waterfall['waterfall_items']) == 6

def test_multilingual_loan_agent():
    # Test Tamil intent
    ta_res = process_voice_intent('VND-1001', 'ta', vendor_profile={'vendor_name': 'Karthik S.', 'business_type': 'Chai & Snacks', 'city': 'Madurai'})
    assert ta_res['language_code'] == 'ta'
    assert 'வணக்கம்' in ta_res['readback_verification_text']
    assert ta_res['loan_amount_requested'] == 20000.0
    assert len(ta_res['fields_provenance']) >= 5

    # Test audit chain integrity
    confirmed = verify_and_confirm_application('VND-1001', ta_res, ta_res['audit_hash'])
    assert confirmed['status'] == 'SUBMITTED_TO_PORTAL'
    assert confirmed['readback_status'] == 'CONFIRMED'
    assert len(confirmed['audit_hash']) == 64

def test_account_aggregator():
    status = aa_engine.get_consent_status('VND-1001')
    assert status['status'] == 'ACTIVE'
    assert 'verified_bank_name' in status

def test_api_loan_and_aa_endpoints():
    # 1. Assessment returns quantiles and waterfall
    res_asm = client.get('/api/vendors/VND-1001/assessment')
    assert res_asm.status_code == 200
    asm_data = res_asm.json()
    assert 'p10_score' in asm_data
    assert 'waterfall' in asm_data
    assert asm_data['waterfall']['base_score'] == 620

    # 2. Voice intent endpoint
    res_voice = client.post('/api/vendors/VND-1001/loan-application/voice-intent', json={'language_code': 'hi'})
    assert res_voice.status_code == 200
    voice_data = res_voice.json()
    assert voice_data['extracted_intent'] == 'APPLY_LOAN'

    # 3. AA consent status
    res_aa = client.get('/api/aa/consent/VND-1001/status')
    assert res_aa.status_code == 200
    assert res_aa.json()['status'] == 'ACTIVE'
