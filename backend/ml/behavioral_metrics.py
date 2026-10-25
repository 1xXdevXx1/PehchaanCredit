import pandas as pd
import numpy as np
import math

def compute_circular_stats(hours: pd.Series) -> dict:
    """
    Computes circular statistics on 24-hour timestamps:
    theta_i = (hour_i / 24) * 2 * pi
    C = (1/n) * sum(cos(theta_i))
    S = (1/n) * sum(sin(theta_i))
    R = sqrt(C^2 + S^2)
    Circular Variance = 1 - R
    Circular Mean Hour = (atan2(S, C) / (2*pi)) * 24
    """
    if len(hours) == 0:
        return {
            'R': 0.5,
            'circular_variance': 0.5,
            'circular_mean_hour': 12.0,
            'consistency': 0.5
        }
    
    thetas = (hours.astype(float) / 24.0) * 2.0 * np.pi
    C = float(np.mean(np.cos(thetas)))
    S = float(np.mean(np.sin(thetas)))
    R = float(np.sqrt(C**2 + S**2))
    R = max(0.0, min(1.0, R))
    
    circular_variance = 1.0 - R
    mean_angle = math.atan2(S, C)
    if mean_angle < 0:
        mean_angle += 2.0 * np.pi
    circular_mean_hour = (mean_angle / (2.0 * np.pi)) * 24.0
    
    return {
        'R': round(R, 4),
        'circular_variance': round(circular_variance, 4),
        'circular_mean_hour': round(circular_mean_hour, 2),
        'consistency': round(R, 4)
    }

def compute_shannon_entropy(hours: pd.Series, bins: int = 24) -> dict:
    """
    Computes Shannon Entropy on hourly transaction distributions:
    p_h = count(h) / N
    H = - sum(p_h * log2(p_h)) for p_h > 0
    H_max = log2(24) = 4.58496
    Normalized concentration = 1 - (H / H_max)
    """
    if len(hours) == 0:
        return {'entropy': 0.0, 'entropy_concentration': 0.5, 'normalized_entropy': 1.0}
        
    counts = hours.value_counts()
    N = len(hours)
    probs = counts / N
    probs = probs[probs > 0]
    
    H = -float(np.sum(probs * np.log2(probs)))
    H_max = np.log2(bins)
    norm_H = max(0.0, min(1.0, H / H_max))
    entropy_concentration = max(0.0, min(1.0, 1.0 - norm_H))
    
    return {
        'entropy': round(H, 4),
        'normalized_entropy': round(norm_H, 4),
        'entropy_concentration': round(entropy_concentration, 4)
    }

def compute_haversine_dispersion(lats: pd.Series, lons: pd.Series) -> float:
    """
    Computes approximate spatial geo-dispersion in kilometers using haversine metric.
    """
    if len(lats) < 2 or len(lons) < 2 or lats.isna().all() or lons.isna().all():
        return 0.0
        
    lat_rad = np.radians(lats.dropna())
    lon_rad = np.radians(lons.dropna())
    if len(lat_rad) < 2:
        return 0.0
        
    lat_std_km = float(lat_rad.std() * 6371.0)
    lon_std_km = float(lon_rad.std() * 6371.0 * np.cos(lat_rad.mean()))
    dispersion = float(np.sqrt(lat_std_km**2 + lon_std_km**2))
    return round(dispersion, 4)

def compute_legacy_indices(df_tx_vendor: pd.DataFrame, days_total: int = 365) -> dict:
    if len(df_tx_vendor) == 0:
        return {'fsi': 0.0, 'tci': 0.0, 'bgi': 0.0, 'fri': 0.0}
        
    # 1. FSI - Financial Stability Index
    df = df_tx_vendor.copy()
    df['month'] = pd.to_datetime(df['timestamp']).dt.to_period('M')
    monthly_in = df[df['transaction_type'] == 'CUSTOMER_PAYMENT'].groupby('month')['amount'].sum()
    if len(monthly_in) > 1 and monthly_in.mean() > 0:
        cv = monthly_in.std() / monthly_in.mean()
        fsi = max(0.1, min(1.0, 1.0 - (cv / 2.0)))
    else:
        fsi = 0.5
        
    # 2. TCI - Transaction Consistency Index
    active_days = df['timestamp'].dt.date.nunique()
    tci = max(0.1, min(1.0, active_days / max(30, days_total * 0.85)))
    
    # 3. BGI - Business Growth Index
    if len(monthly_in) >= 3:
        first_half = monthly_in.iloc[:len(monthly_in)//2].mean()
        second_half = monthly_in.iloc[len(monthly_in)//2:].mean()
        growth = (second_half - first_half) / (first_half + 1e-5)
        bgi = max(0.0, min(1.0, 0.5 + (growth * 0.5)))
    else:
        bgi = 0.5
        
    # 4. FRI - Fraud Risk Index
    night_ratio = len(df[df['hour'].isin([23, 0, 1, 2, 3, 4])]) / len(df)
    cust_tx = df[df['transaction_type'] == 'CUSTOMER_PAYMENT']
    conc = cust_tx['counterparty_id'].value_counts().iloc[0] / len(cust_tx) if len(cust_tx) > 0 else 0
    fri = max(0.0, min(1.0, (night_ratio * 0.5) + (conc * 0.5)))
    
    return {
        'fsi': round(float(fsi), 4),
        'tci': round(float(tci), 4),
        'bgi': round(float(bgi), 4),
        'fri': round(float(fri), 4)
    }

def compute_framework_metrics(df_tx_vendor: pd.DataFrame, stl_resilience: float = 0.90) -> dict:
    if len(df_tx_vendor) == 0:
        return {
            'spv': 0.5, 'tsci': 0.5, 'mcs': 0.5, 'resilience': 0.9,
            'mandi_r': 0.5, 'circular_variance_supp': 0.5,
            'circular_variance_cust': 0.5, 'shannon_entropy': 0.0,
            'entropy_concentration': 0.5, 'cdr': 0.5, 'reciprocity_ratio': 0.0
        }
        
    df = df_tx_vendor.copy()
    
    # --- 1. SPV (Supplier Payment Velocity) with Mandi Circular Statistics ---
    outbound = df[df['transaction_type'].isin(['SUPPLIER_PAYMENT', 'TRANSFER'])]
    supp_tx = df[df['transaction_type'] == 'SUPPLIER_PAYMENT']
    supp_payments = supp_tx['amount'].sum()
    total_outbound = outbound['amount'].sum()
    
    if total_outbound > 0:
        base_spv = float(supp_payments / total_outbound)
    else:
        base_spv = 0.70
        
    supp_hours = supp_tx['hour'] if len(supp_tx) > 0 else pd.Series([6, 7])
    supp_circ = compute_circular_stats(supp_hours)
    mandi_r = supp_circ['R']
    circ_var_supp = supp_circ['circular_variance']
    
    spv = base_spv * (0.75 + 0.25 * mandi_r)
    spv = max(0.05, min(0.98, spv))
    
    # --- 2. TSCI (Business Rhythm) with Circular Variance & Peak-Hour Shannon Entropy ---
    dates = pd.to_datetime(df['date'])
    date_range = (dates.max() - dates.min()).days + 1 if len(dates) > 1 else 1
    temporal = min(1.0, df['date'].nunique() / max(1, date_range * 0.8))
    
    cust_tx = df[df['transaction_type'] == 'CUSTOMER_PAYMENT']
    cust_hours = cust_tx['hour'] if len(cust_tx) > 0 else df['hour']
    cust_circ = compute_circular_stats(cust_hours)
    cv_customer = cust_circ['circular_variance']
    
    entropy_info = compute_shannon_entropy(cust_hours)
    entropy_conc = entropy_info['entropy_concentration']
    
    lats = df['latitude'] if 'latitude' in df.columns else pd.Series([])
    lons = df['longitude'] if 'longitude' in df.columns else pd.Series([])
    dispersion = compute_haversine_dispersion(lats, lons)
    geo_consistency = max(0.1, 1.0 - min(1.0, dispersion * 0.1))
    
    tsci = (0.35 * temporal) + (0.25 * (1.0 - cv_customer)) + (0.25 * entropy_conc) + (0.15 * geo_consistency)
    tsci = max(0.1, min(0.98, tsci))
    
    # --- 3. MCS (Merchant Customer Score) with CDR, Reciprocity Filter, and Gaussian Recurrence ---
    if len(cust_tx) > 0:
        unique_c = cust_tx['counterparty_id'].nunique()
        total_cust_tx = len(cust_tx)
        
        cdr = min(1.0, unique_c / max(1, total_cust_tx))
        diversity = min(1.0, unique_c / 50.0)
        
        vc = cust_tx['counterparty_id'].value_counts()
        recurring_count = len(vc[(vc >= 2) & (vc <= 15)])
        recurrence_rate = recurring_count / max(1, unique_c)
        gaussian_recurrence = math.exp(-((recurrence_rate - 0.30) ** 2) / (2 * (0.20 ** 2)))
        
        in_c = set(cust_tx['counterparty_id'])
        out_c = set(outbound['counterparty_id'])
        reciprocal_ids = in_c.intersection(out_c)
        
        reciprocal_volume = 0.0
        for cp in reciprocal_ids:
            cp_in = cust_tx[cust_tx['counterparty_id'] == cp]['amount'].sum()
            cp_out = outbound[outbound['counterparty_id'] == cp]['amount'].sum()
            if cp_out > 0 and (min(cp_in, cp_out) / max(cp_in, cp_out)) > 0.30:
                reciprocal_volume += cp_in
                
        reciprocity_ratio = reciprocal_volume / max(1.0, cust_tx['amount'].sum())
        reciprocity_penalty = min(1.0, reciprocity_ratio * 2.0)
        
        mcs = (0.35 * diversity) + (0.35 * gaussian_recurrence) + (0.20 * cdr) - (0.30 * reciprocity_penalty)
        mcs = max(0.1, min(0.98, mcs))
    else:
        cdr = 0.5
        reciprocity_ratio = 0.0
        mcs = 0.5
        
    return {
        'spv': round(float(spv), 4),
        'tsci': round(float(tsci), 4),
        'mcs': round(float(mcs), 4),
        'resilience': round(float(stl_resilience), 4),
        'mandi_r': round(float(mandi_r), 4),
        'circular_variance_supp': round(float(circ_var_supp), 4),
        'circular_variance_cust': round(float(cv_customer), 4),
        'shannon_entropy': round(float(entropy_info['entropy']), 4),
        'entropy_concentration': round(float(entropy_conc), 4),
        'cdr': round(float(cdr), 4),
        'reciprocity_ratio': round(float(reciprocity_ratio), 4)
    }
