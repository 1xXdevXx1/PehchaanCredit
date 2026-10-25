import pandas as pd
import numpy as np
from datetime import datetime

def clean_transactions(df_tx: pd.DataFrame) -> pd.DataFrame:
    # 1. Drop duplicates
    df = df_tx.drop_duplicates(subset=['transaction_id']).copy()
    
    # 2. Filter valid amounts
    df = df[df['amount'] > 0]
    
    # 3. Parse timestamp
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = df.dropna(subset=['timestamp'])
    
    # 4. Normalize categories
    df['payment_channel'] = df['payment_channel'].fillna('UPI').str.upper()
    df['transaction_type'] = df['transaction_type'].fillna('CUSTOMER_PAYMENT').str.upper()
    
    # 5. Extract temporal components
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    df['date'] = df['timestamp'].dt.date
    
    df = df.sort_values('timestamp').reset_index(drop=True)
    return df

def clean_vendors(df_v: pd.DataFrame) -> pd.DataFrame:
    df = df_v.drop_duplicates(subset=['vendor_id']).copy()
    df['vendor_age'] = df['vendor_age'].fillna(35).clip(18, 90)
    df['business_age_months'] = df['business_age_months'].fillna(12).clip(1, 600)
    return df
