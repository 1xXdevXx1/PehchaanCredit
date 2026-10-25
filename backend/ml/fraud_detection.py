import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

def evaluate_fraud_rules(df_tx_vendor: pd.DataFrame) -> dict:
    if len(df_tx_vendor) == 0:
        return {'rule_flags': [], 'rule_score': 0.0, 'evidence': []}
        
    flags = []
    evidence = []
    rule_penalties = 0.0
    
    # 1. Repeated identical amounts
    amt_counts = df_tx_vendor['amount'].value_counts()
    if len(amt_counts) > 0:
        top_amt = amt_counts.index[0]
        top_amt_freq = amt_counts.iloc[0]
        if top_amt_freq >= 15 and (top_amt_freq / len(df_tx_vendor)) > 0.35 and top_amt > 1000:
            flags.append('REPEATED_AMOUNTS')
            evidence.append(f'High concentration of identical ₹{top_amt:,.0f} transactions ({top_amt_freq} times)')
            rule_penalties += 0.25
            
    # 2. Night transactions (11 PM - 4 AM)
    night_tx = df_tx_vendor[df_tx_vendor['hour'].isin([23, 0, 1, 2, 3, 4])]
    night_ratio = len(night_tx) / len(df_tx_vendor)
    if night_ratio > 0.20 and len(night_tx) > 10:
        flags.append('EXCESSIVE_NIGHT_TX')
        evidence.append(f'Abnormal night-time activity ({night_ratio*100:.1f}% of transactions between 11 PM - 4 AM)')
        rule_penalties += 0.20
        
    # 3. Low customer diversity / Heavy counterparty concentration
    cust_tx = df_tx_vendor[df_tx_vendor['transaction_type'] == 'CUSTOMER_PAYMENT']
    if len(cust_tx) >= 20:
        top_cust_ratio = cust_tx['counterparty_id'].value_counts().iloc[0] / len(cust_tx)
        if top_cust_ratio > 0.40:
            flags.append('CUSTOMER_CONCENTRATION')
            evidence.append(f'Severe customer concentration: single party accounts for {top_cust_ratio*100:.1f}% of volume')
            rule_penalties += 0.25
            
    # 4. Sudden volume spike
    # Check if any single day has > 5x median daily volume
    daily_vol = df_tx_vendor.groupby('date')['amount'].sum()
    if len(daily_vol) >= 10:
        med_v = daily_vol.median()
        max_v = daily_vol.max()
        if med_v > 0 and (max_v / med_v) > 6.0 and max_v > 50000:
            flags.append('VOLUME_SPIKE')
            evidence.append(f'Sudden single-day spike: ₹{max_v:,.0f} vs median daily ₹{med_v:,.0f}')
            rule_penalties += 0.15
            
    rule_score = min(1.0, rule_penalties)
    return {
        'rule_flags': flags,
        'rule_score': round(rule_score, 4),
        'evidence': evidence
    }

class IsolationForestDetector:
    def __init__(self):
        self.model = IsolationForest(n_estimators=100, contamination=0.08, random_state=42)
        self.is_fitted = False
        
    def fit(self, X_features: pd.DataFrame):
        feat_cols = ['total_volume', 'tx_count', 'avg_amount', 'std_amount', 
                     'customer_concentration', 'night_ratio']
        X = X_features[feat_cols].fillna(0)
        self.model.fit(X)
        self.is_fitted = True
        
    def predict_anomaly_score(self, vendor_feature_row: pd.Series) -> float:
        if not self.is_fitted:
            return 0.05
        feat_cols = ['total_volume', 'tx_count', 'avg_amount', 'std_amount', 
                     'customer_concentration', 'night_ratio']
        X = pd.DataFrame([vendor_feature_row[feat_cols].fillna(0)])
        # decision_function gives negative for anomalies
        raw_score = self.model.decision_function(X)[0]
        # Map roughly from [-0.5, 0.5] to [1.0 (anomaly), 0.0 (normal)]
        norm_score = max(0.0, min(1.0, 0.5 - raw_score))
        return round(float(norm_score), 4)

def compute_svps(rule_score: float, anomaly_score: float, graph_data: dict) -> dict:
    penalty = 0.0
    evidence = []
    
    # Rules contribution (weight: 0.40)
    penalty += (rule_score * 0.40)
    
    # Isolation forest anomaly contribution (weight: 0.25)
    penalty += (anomaly_score * 0.25)
    
    # Graph cycle contribution (weight: 0.35)
    if graph_data.get('has_cycles', False):
        penalty += 0.30
        evidence.append('Circular fund routing loop identified')
    if graph_data.get('reciprocal_count', 0) > 0:
        penalty += 0.15
        evidence.append('Reciprocal counterparty fund bouncing')
        
    svps = max(0.0, min(1.0, penalty))
    
    return {
        'svps': round(svps, 4),
        'penalty_percentage': round(svps * 100, 1),
        'adjusted_volume_factor': round(1.0 - svps, 4),
        'fraud_risk_band': 'Low' if svps < 0.15 else ('Moderate' if svps < 0.30 else 'Elevated')
    }
