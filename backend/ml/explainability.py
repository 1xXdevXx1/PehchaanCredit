import pandas as pd
import numpy as np

def explain_prediction(model_wrapper, X_row: pd.Series) -> dict:
    positive = []
    negative = []
    
    spv_val = float(X_row.get('spv', 0))
    if spv_val >= 0.75:
        positive.append('Stable supplier payment velocity supporting authentic business operations')
    elif spv_val < 0.40:
        negative.append('Low supplier payment ratio relative to outward transfers')
        
    tsci_val = float(X_row.get('tsci', 0))
    if tsci_val >= 0.75:
        positive.append('Consistent business rhythm and plausible operating hours')
    elif tsci_val < 0.50:
        negative.append('Irregular operating schedule or frequent inactive periods')
        
    mcs_val = float(X_row.get('mcs', 0))
    if mcs_val >= 0.75:
        positive.append('High customer diversity with healthy repeat visit recurrence')
    elif mcs_val < 0.50:
        negative.append('High customer concentration or reciprocal counterparty risk')
        
    res_val = float(X_row.get('resilience', 1.0))
    if res_val >= 0.90:
        positive.append('Strong seasonal resilience during expected business fluctuations')
    else:
        negative.append('Lower than expected revenue during peak seasonal period')
        
    svps_val = float(X_row.get('svps', 0))
    if svps_val > 0.15:
        negative.append(f'Suspicious volume penalty ({svps_val*100:.0f}%) applied')
        
    if not positive:
        positive.append('Minimum operational transaction activity recorded')
    if not negative:
        negative.append('No significant negative behavioral anomalies flagged')
        
    return {
        'top_positive_factors': positive,
        'top_negative_factors': negative
    }
