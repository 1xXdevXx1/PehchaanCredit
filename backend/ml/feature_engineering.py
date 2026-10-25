import pandas as pd
import numpy as np

def extract_vendor_features(df_tx: pd.DataFrame, df_vendors: pd.DataFrame) -> pd.DataFrame:
    features = []
    
    grouped = df_tx.groupby('vendor_id')
    
    for _, v in df_vendors.iterrows():
        v_id = v['vendor_id']
        if v_id not in grouped.groups:
            # Fallback zero-features
            features.append({
                'vendor_id': v_id,
                'total_volume': 0.0,
                'tx_count': 0,
                'avg_amount': 0.0,
                'median_amount': 0.0,
                'std_amount': 0.0,
                'active_days': 0,
                'unique_customers': 0,
                'customer_concentration': 0.0,
                'supplier_tx_count': 0,
                'supplier_volume': 0.0,
                'night_ratio': 0.0,
                'weekend_ratio': 0.0
            })
            continue
            
        tx_v = grouped.get_group(v_id)
        
        amounts = tx_v['amount']
        tot_vol = float(amounts.sum())
        count = len(tx_v)
        avg_amt = float(amounts.mean())
        med_amt = float(amounts.median())
        std_amt = float(amounts.std()) if count > 1 else 0.0
        active_days = tx_v['date'].nunique()
        
        # Customers
        cust_tx = tx_v[tx_v['transaction_type'] == 'CUSTOMER_PAYMENT']
        u_cust = cust_tx['counterparty_id'].nunique()
        if len(cust_tx) > 0:
            top_cust_freq = cust_tx['counterparty_id'].value_counts().iloc[0]
            cust_concentration = float(top_cust_freq / len(cust_tx))
        else:
            cust_concentration = 0.0
            
        # Suppliers
        supp_tx = tx_v[tx_v['transaction_type'] == 'SUPPLIER_PAYMENT']
        supp_count = len(supp_tx)
        supp_vol = float(supp_tx['amount'].sum())
        
        # Temporal
        night_count = len(tx_v[tx_v['hour'].isin([23, 0, 1, 2, 3, 4])])
        night_ratio = float(night_count / count) if count > 0 else 0.0
        weekend_count = len(tx_v[tx_v['is_weekend'] == 1])
        weekend_ratio = float(weekend_count / count) if count > 0 else 0.0
        
        features.append({
            'vendor_id': v_id,
            'total_volume': tot_vol,
            'tx_count': count,
            'avg_amount': round(avg_amt, 2),
            'median_amount': round(med_amt, 2),
            'std_amount': round(std_amt, 2),
            'active_days': active_days,
            'unique_customers': u_cust,
            'customer_concentration': round(cust_concentration, 4),
            'supplier_tx_count': supp_count,
            'supplier_volume': supp_vol,
            'night_ratio': round(night_ratio, 4),
            'weekend_ratio': round(weekend_ratio, 4)
        })
        
    df_feat = pd.DataFrame(features)
    return pd.merge(df_vendors[['vendor_id', 'business_type', 'city', 'archetype']], df_feat, on='vendor_id')
