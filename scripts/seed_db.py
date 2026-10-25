import json
from datetime import datetime
import pandas as pd
from backend.app.database import init_db, SessionLocal
from backend.app.models.schema_models import Vendor, Transaction, Assessment
from backend.ml.preprocessing import clean_transactions, clean_vendors
from backend.ml.feature_engineering import extract_vendor_features
from backend.ml.behavioral_metrics import compute_legacy_indices, compute_framework_metrics
from backend.ml.seasonality import compute_resilience_stl
from backend.ml.graph_analysis import build_transaction_graph, analyze_vendor_graph
from backend.ml.fraud_detection import evaluate_fraud_rules, IsolationForestDetector, compute_svps
from backend.ml.scoring import compute_final_credit_score, compute_behavioral_trust_score
from backend.ml.decision_engine import make_lender_decision
from backend.ml.explainability import explain_prediction
from backend.ml.model import CreditModel

def seed():
    print('Initializing database schema...')
    init_db()
    db = SessionLocal()
    
    # Check if vendors exist
    if db.query(Vendor).count() > 0:
        print('Database already seeded.')
        db.close()
        return
        
    print('Loading synthetic CSVs for seeding...')
    df_v = pd.read_csv('data/synthetic/vendors.csv')
    df_tx = pd.read_csv('data/synthetic/transactions.csv')
    
    # Clean
    df_v_clean = clean_vendors(df_v)
    df_tx_clean = clean_transactions(df_tx)
    
    print(f'Seeding {len(df_v_clean)} vendors into SQLite...')
    for _, r in df_v_clean.iterrows():
        db.add(Vendor(
            vendor_id=r['vendor_id'],
            vendor_name=r['vendor_name'],
            business_type=r['business_type'],
            city=r['city'],
            vendor_age=int(r['vendor_age']),
            business_age_months=int(r['business_age_months']),
            archetype=r['archetype']
        ))
    db.commit()
    
    print('Seeding recent 5,000 transactions for fast prototype demo...')
    sample_tx = df_tx_clean.tail(5000)
    for _, r in sample_tx.iterrows():
        db.add(Transaction(
            transaction_id=r['transaction_id'],
            timestamp=str(r['timestamp']),
            vendor_id=r['vendor_id'],
            counterparty_id=r['counterparty_id'],
            transaction_type=r['transaction_type'],
            amount=float(r['amount']),
            payment_channel=r['payment_channel'],
            business_type=r.get('business_type', ''),
            city=r.get('city', ''),
            latitude=float(r.get('latitude', 12.9165)),
            longitude=float(r.get('longitude', 79.1325))
        ))
    db.commit()
    
    print('Precomputing assessments for top demo vendors...')
    G = build_transaction_graph(df_tx_clean)
    df_features = extract_vendor_features(df_tx_clean, df_v_clean)
    iso = IsolationForestDetector()
    iso.fit(df_features)
    
    model = CreditModel(model_dir='models')
    model.load()
    
    tx_by_v = df_tx_clean.groupby('vendor_id')
    
    for _, v_row in df_features.iterrows():
        v_id = v_row['vendor_id']
        tx_v = tx_by_v.get_group(v_id) if v_id in tx_by_v.groups else pd.DataFrame()
        
        legacy = compute_legacy_indices(tx_v)
        stl = compute_resilience_stl(tx_v)
        framework = compute_framework_metrics(tx_v, stl_resilience=stl['resilience'])
        graph_info = analyze_vendor_graph(G, v_id)
        rules = evaluate_fraud_rules(tx_v)
        anom = iso.predict_anomaly_score(v_row)
        svps_info = compute_svps(rules['rule_score'], anom, graph_info)
        
        row_feat = pd.Series({
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
        })
        
        q_base = model.predict_q_base(row_feat)
        score_info = compute_final_credit_score(q_base, svps_info['svps'])
        trust_score = compute_behavioral_trust_score(
            framework['spv'], framework['tsci'], framework['mcs'], framework['resilience'], svps_info['svps']
        )
        dec = make_lender_decision(score_info['credit_score'], svps_info['svps'], score_info['rating'], rules['rule_flags'])
        expl = explain_prediction(model, row_feat)
        
        db.add(Assessment(
            vendor_id=v_id,
            credit_score=score_info['credit_score'],
            rating=score_info['rating'],
            behavioral_trust=trust_score,
            q_base=score_info['q_base'],
            q_final=score_info['q_final'],
            svps=score_info['svps'],
            fraud_risk=svps_info['svps'],
            decision=dec['decision'],
            action=dec['action'],
            spv=framework['spv'],
            tsci=framework['tsci'],
            mcs=framework['mcs'],
            resilience=framework['resilience'],
            fsi=legacy['fsi'],
            tci=legacy['tci'],
            bgi=legacy['bgi'],
            fri=legacy['fri'],
            explanation_json=json.dumps(expl),
            created_at=datetime.utcnow().isoformat()
        ))
    db.commit()
    db.close()
    print('Database seeded successfully!')

if __name__ == '__main__':
    seed()
