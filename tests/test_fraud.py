import pytest
import pandas as pd
import networkx as nx
from backend.ml.graph_analysis import build_transaction_graph, analyze_vendor_graph
from backend.ml.fraud_detection import evaluate_fraud_rules, compute_svps

def test_circular_graph_cycle_detection():
    # Inject known circle: A -> B -> C -> A
    df = pd.DataFrame([
        {'vendor_id': 'A', 'counterparty_id': 'B', 'amount': 5000},
        {'vendor_id': 'B', 'counterparty_id': 'C', 'amount': 5000},
        {'vendor_id': 'C', 'counterparty_id': 'A', 'amount': 5000}
    ])
    G = build_transaction_graph(df)
    analysis_A = analyze_vendor_graph(G, 'A')
    assert analysis_A['has_cycles'] is True
    assert analysis_A['cycle_count'] >= 1

def test_fraud_rule_repeated_amounts():
    df = pd.DataFrame([
        {'amount': 5000, 'hour': 14, 'date': '2026-09-01', 'transaction_type': 'CUSTOMER_PAYMENT', 'counterparty_id': 'C1'}
        for _ in range(25)
    ])
    rules = evaluate_fraud_rules(df)
    assert 'REPEATED_AMOUNTS' in rules['rule_flags']
    assert rules['rule_score'] > 0