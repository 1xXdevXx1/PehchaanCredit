import pandas as pd
import numpy as np
from datetime import datetime

# Major Tamil Nadu & National festival dates for seasonality normalization
TAMIL_NADU_FESTIVALS = [
    '2026-01-14', '2026-01-15', # Pongal / Makar Sankranti
    '2026-03-20',               # Eid-ul-Fitr / Ugadi
    '2026-04-14',               # Tamil New Year (Puthandu)
    '2026-08-28',               # Onam / Milad-un-Nabi
    '2026-09-14',               # Vinayaka Chaturthi
    '2026-10-19', '2026-10-20', # Ayudha Puja / Dussehra
    '2026-11-08',               # Deepavali
    '2026-12-25'                # Christmas
]

def get_festival_covariates(date_series: pd.Series) -> pd.DataFrame:
    """
    Computes festival indicator and days-to-next-festival for each transaction date.
    """
    fest_dates = [pd.to_datetime(d).date() for d in TAMIL_NADU_FESTIVALS]
    dates = pd.to_datetime(date_series).dt.date
    
    is_fest = dates.isin(fest_dates).astype(int)
    
    # Days to nearest festival
    days_to_fest = []
    for d in dates:
        deltas = [abs((d - fd).days) for fd in fest_dates]
        days_to_fest.append(min(deltas) if deltas else 30)
        
    return pd.DataFrame({
        'is_festival': is_fest,
        'days_to_festival': days_to_fest
    })

def compute_resilience_stl(df_tx_vendor: pd.DataFrame, city: str = 'Chennai') -> dict:
    if len(df_tx_vendor) == 0:
        return {
            'resilience': 0.90, 'method': 'FALLBACK_INSUFFICIENT_DATA', 
            'is_seasonal': False, 'monsoon_resilience': 0.88,
            'festival_uplift': 1.15
        }
        
    df = df_tx_vendor[df_tx_vendor['transaction_type'] == 'CUSTOMER_PAYMENT'].copy()
    if len(df) < 30:
        return {
            'resilience': 0.88, 'method': 'ROBUST_FALLBACK_SHORT_HISTORY', 
            'is_seasonal': False, 'monsoon_resilience': 0.85,
            'festival_uplift': 1.12
        }
        
    # Aggregate daily
    daily = df.groupby('date')['amount'].sum().reset_index()
    daily['date'] = pd.to_datetime(daily['date'])
    daily = daily.sort_values('date').set_index('date')
    
    # Reindex continuous daily sequence
    idx = pd.date_range(daily.index.min(), daily.index.max())
    daily = daily.reindex(idx, fill_value=0.0)
    
    # Evaluate weather and monsoon season (Oct - Dec in Tamil Nadu Northeast Monsoon)
    daily['month'] = daily.index.month
    monsoon_days = daily[daily['month'].isin([10, 11, 12])]
    non_monsoon_days = daily[~daily['month'].isin([10, 11, 12])]
    
    if len(monsoon_days) > 0 and len(non_monsoon_days) > 0:
        monsoon_mean = monsoon_days['amount'].mean()
        normal_mean = non_monsoon_days['amount'].mean()
        monsoon_resilience = float(monsoon_mean / (normal_mean + 1e-5)) if normal_mean > 0 else 0.85
    else:
        monsoon_resilience = 0.88
        
    # Check if history is sufficient for STL (>= 60 days)
    if len(daily) >= 60:
        try:
            from statsmodels.tsa.seasonal import STL
            res = STL(daily['amount'], period=7, robust=True).fit()
            trend = res.trend
            seasonal = res.seasonal
            expected = trend + seasonal
            expected = expected.clip(lower=10.0)
            
            # Resilience = Actual / Expected
            ratio = daily['amount'] / expected
            resilience = float(ratio.median())
            resilience = max(0.4, min(1.3, resilience))
            is_seasonal = float(np.std(seasonal)) > 0.15 * float(np.mean(trend) + 1e-5)
            
            # Incorporate monsoon weather resilience factor
            adjusted_resilience = 0.70 * resilience + 0.30 * min(1.1, monsoon_resilience)
            
            return {
                'resilience': round(float(adjusted_resilience), 4),
                'raw_stl_resilience': round(float(resilience), 4),
                'method': 'STL_DECOMPOSITION_WITH_WEATHER',
                'is_seasonal': is_seasonal,
                'monsoon_resilience': round(float(monsoon_resilience), 4),
                'festival_uplift': 1.18
            }
        except Exception as e:
            pass
            
    # Fallback ratio comparison
    mean_val = daily['amount'].mean()
    med_val = daily['amount'].median()
    resilience = (med_val / (mean_val + 1e-5)) if mean_val > 0 else 0.85
    resilience = max(0.5, min(1.2, resilience))
    return {
        'resilience': round(float(resilience), 4),
        'method': 'MEDIAN_MEAN_RATIO_FALLBACK',
        'is_seasonal': False,
        'monsoon_resilience': round(float(monsoon_resilience), 4),
        'festival_uplift': 1.12
    }

