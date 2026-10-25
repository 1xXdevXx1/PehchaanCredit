import json
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from backend.ml.preprocessing import clean_transactions, clean_vendors
from backend.ml.feature_engineering import extract_vendor_features
from backend.ml.behavioral_metrics import compute_legacy_indices, compute_framework_metrics
from backend.ml.seasonality import compute_resilience_stl
from backend.ml.graph_analysis import build_transaction_graph, analyze_vendor_graph
from backend.ml.fraud_detection import evaluate_fraud_rules, IsolationForestDetector, compute_svps
from backend.ml.model import CreditModel

def train():
    print('Loading synthetic data...')
    df_vendors = pd.read_csv('data/synthetic/vendors.csv')
    df_tx = pd.read_csv('data/synthetic/transactions.csv')
    df_labels = pd.read_csv('data/synthetic/repayment_labels.csv')
    
    print('Cleaning & preprocessing...')
    df_tx_clean = clean_transactions(df_tx)
    df_v_clean = clean_vendors(df_vendors)
    
    print('Building transaction network graph...')
    G = build_transaction_graph(df_tx_clean)
    
    print('Extracting features and behavioral indices...')
    df_features = extract_vendor_features(df_tx_clean, df_v_clean)
    
    # Fit Isolation Forest on vendor aggregate features
    iso_detector = IsolationForestDetector()
    iso_detector.fit(df_features)
    
    # Compute per-vendor metrics
    metric_rows = []
    tx_by_v = df_tx_clean.groupby('vendor_id')
    
    for _, v_row in df_features.iterrows():
        v_id = v_row['vendor_id']
        tx_v = tx_by_v.get_group(v_id) if v_id in tx_by_v.groups else pd.DataFrame()
        
        # Legacy
        legacy = compute_legacy_indices(tx_v)
        # STL
        stl_res = compute_resilience_stl(tx_v)
        # Framework
        framework = compute_framework_metrics(tx_v, stl_resilience=stl_res['resilience'])
        # Graph
        graph_info = analyze_vendor_graph(G, v_id)
        # Rules
        rules = evaluate_fraud_rules(tx_v)
        # Anomaly
        anom_score = iso_detector.predict_anomaly_score(v_row)
        # SVPS
        svps_info = compute_svps(rules['rule_score'], anom_score, graph_info)
        
        row_dict = {
            'vendor_id': v_id,
            'spv': framework['spv'],
            'tsci': framework['tsci'],
            'mcs': framework['mcs'],
            'resilience': framework['resilience'],
            'fsi': legacy['fsi'],
            'tci': legacy['tci'],
            'bgi': legacy['bgi'],
            'fri': legacy['fri'],
            'svps': svps_info['svps'],
            'total_volume': v_row['total_volume'],
            'tx_count': v_row['tx_count'],
            'avg_amount': v_row['avg_amount'],
            'unique_customers': v_row['unique_customers']
        }
        metric_rows.append(row_dict)
        
    df_metrics = pd.DataFrame(metric_rows)
    df_train = pd.merge(df_metrics, df_labels[['vendor_id', 'repayment_probability']], on='vendor_id')
    
    X = df_train[CreditModel().feature_cols]
    y = df_train['repayment_probability']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print('Training XGBoost model...')
    model = CreditModel(model_dir='models')
    model.fit(X_train, y_train)
    model.save()
    
    preds = model.model.predict(X_test)
    mse = float(mean_squared_error(y_test, preds))
    r2 = float(r2_score(y_test, preds))
    
    metrics = {
        'model_type': 'XGBoostRegressor',
        'target': 'repayment_probability (synthetic)',
        'test_mse': round(mse, 4),
        'test_r2': round(r2, 4),
        'sample_size': len(df_train),
        'features': CreditModel().feature_cols,
        'status': 'TRAINED'
    }
    
    with open('models/model_metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)
        
    print(f'Model trained successfully! Test MSE: {mse:.4f}, R2: {r2:.4f}')
    print('Artifacts saved in models/')

if __name__ == '__main__':
    train()
