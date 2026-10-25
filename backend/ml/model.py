import json
import os
import joblib
import pandas as pd
import numpy as np
import xgboost as xgb

class CreditModel:
    def __init__(self, model_dir='models'):
        self.model_dir = model_dir
        self.model = None
        self.feature_cols = [
            'spv', 'tsci', 'mcs', 'resilience', 
            'fsi', 'tci', 'bgi', 'fri', 'svps', 
            'total_volume', 'tx_count', 'avg_amount', 'unique_customers'
        ]
        
    def fit(self, X: pd.DataFrame, y: pd.Series):
        X_clean = X[self.feature_cols].fillna(0)
        self.model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.08,
            random_state=42
        )
        self.model.fit(X_clean, y)
        
    def predict_q_base(self, X_row: pd.Series) -> float:
        if self.model is None:
            self.load()
            
        feat_df = pd.DataFrame([X_row[self.feature_cols].fillna(0)])
        q = float(self.model.predict(feat_df)[0])
        return max(0.05, min(0.98, q))
        
    def save(self):
        os.makedirs(self.model_dir, exist_ok=True)
        model_path = os.path.join(self.model_dir, 'xgboost_model.json')
        self.model.save_model(model_path)
        with open(os.path.join(self.model_dir, 'feature_metadata.json'), 'w') as f:
            json.dump({'feature_cols': self.feature_cols}, f, indent=2)
            
    def load(self):
        model_path = os.path.join(self.model_dir, 'xgboost_model.json')
        if os.path.exists(model_path):
            self.model = xgb.XGBRegressor()
            self.model.load_model(model_path)
        else:
            raise FileNotFoundError('XGBoost model file not found')
