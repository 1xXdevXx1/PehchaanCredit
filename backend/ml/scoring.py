def compute_final_credit_score(q_base: float, svps: float) -> dict:
    # Formula: Q_final = Q_base * (1 - 0.25 * SVPS)
    q_base_clamped = max(0.0, min(1.0, float(q_base)))
    svps_clamped = max(0.0, min(1.0, float(svps)))
    
    q_final = q_base_clamped * (1.0 - (0.25 * svps_clamped))
    q_final = max(0.0, min(1.0, q_final))
    
    # Formula: Credit Score = 300 + 600 * Q_final
    raw_score = 300.0 + (600.0 * q_final)
    credit_score = int(round(max(300.0, min(900.0, raw_score))))
    
    # Quantile Risk Bands (P10 Conservative, P50 Median, P90 Optimistic)
    # P10: Adverse market/monsoon conditions
    q_p10 = max(0.0, min(1.0, q_final * 0.88 - 0.04))
    p10_score = int(round(max(300.0, min(900.0, 300.0 + 600.0 * q_p10))))
    
    # P50: Normal steady-state operations
    p50_score = credit_score
    
    # P90: Peak festival/seasonal market operations
    q_p90 = max(0.0, min(1.0, q_final * 1.08 + 0.04))
    p90_score = int(round(max(300.0, min(900.0, 300.0 + 600.0 * q_p90))))
    
    # Project-defined rating bands (NOT official CIBIL/RBI)
    if credit_score >= 800:
        rating = 'Excellent'
    elif credit_score >= 750:
        rating = 'Very Good'
    elif credit_score >= 700:
        rating = 'Good'
    elif credit_score >= 650:
        rating = 'Fair'
    elif credit_score >= 600:
        rating = 'Weak'
    else:
        rating = 'Poor'
        
    return {
        'q_base': round(q_base_clamped, 4),
        'svps': round(svps_clamped, 4),
        'q_final': round(q_final, 4),
        'credit_score': credit_score,
        'rating': rating,
        'p10_score': p10_score,
        'p50_score': p50_score,
        'p90_score': p90_score
    }

def compute_itemized_waterfall_statement(credit_score: int, spv: float, tsci: float, mcs: float, resilience: float, svps: float) -> dict:
    """
    Computes an itemized plain-language credit reasoning statement mimicking TreeSHAP attribution:
    e.g. Base 620 + SPV +35 + TSCI +25 + Resilience +18 + MCS +12 - SVPS -10 = Final 700
    """
    base_population_score = 620
    
    # Relative attributions scaled to difference from base population score
    delta_spv = int(round((spv - 0.50) * 100.0))
    delta_tsci = int(round((tsci - 0.50) * 80.0))
    delta_resilience = int(round((min(1.1, resilience) - 0.85) * 80.0))
    delta_mcs = int(round((mcs - 0.50) * 70.0))
    delta_svps = -int(round(svps * 120.0))
    
    # Rebalance sum to exactly match credit_score
    computed_sum = base_population_score + delta_spv + delta_tsci + delta_resilience + delta_mcs + delta_svps
    discrepancy = credit_score - computed_sum
    delta_spv += discrepancy
    
    items = [
        {
            'factor': 'Base Population Baseline',
            'delta': base_population_score,
            'is_base': True,
            'rationale': 'Median unbanked informal vendor credit baseline prior to alternate data'
        },
        {
            'factor': 'Supplier Payment Velocity (SPV)',
            'delta': delta_spv,
            'is_base': False,
            'rationale': 'Consistent morning Mandi wholesale purchases and timely inventory restocking'
        },
        {
            'factor': 'Temporal-Spatial Rhythm (TSCI)',
            'delta': delta_tsci,
            'is_base': False,
            'rationale': 'Daily operating consistency and concentrated peak-hour transaction entropy'
        },
        {
            'factor': 'Seasonality & Weather Resilience',
            'delta': delta_resilience,
            'is_base': False,
            'rationale': 'Robust daily revenue retention during monsoon and festival fluctuations'
        },
        {
            'factor': 'Merchant Customer Score (MCS)',
            'delta': delta_mcs,
            'is_base': False,
            'rationale': 'Healthy customer diversity with repeat neighborhood patrons'
        },
        {
            'factor': 'Synthetic Volume & Collusion Penalty (SVPS)',
            'delta': delta_svps,
            'is_base': False,
            'rationale': 'Adjustment for counterparty concentration or circular payment patterns'
        }
    ]
    
    formula_str = f"{base_population_score} {'+' if delta_spv>=0 else '-'} {abs(delta_spv)} {'+' if delta_tsci>=0 else '-'} {abs(delta_tsci)} {'+' if delta_resilience>=0 else '-'} {abs(delta_resilience)} {'+' if delta_mcs>=0 else '-'} {abs(delta_mcs)} {'-' if delta_svps<=0 else '+'} {abs(delta_svps)} = {credit_score}"
    
    return {
        'base_score': base_population_score,
        'final_score': credit_score,
        'formula_summary': formula_str,
        'waterfall_items': items
    }

def compute_behavioral_trust_score(spv: float, tsci: float, mcs: float, resilience: float, svps: float) -> int:
    raw_trust = (0.25 * spv) + (0.30 * tsci) + (0.25 * mcs) + (0.20 * min(1.0, resilience))
    penalized = raw_trust * (1.0 - (0.5 * svps))
    trust_100 = int(round(max(10.0, min(99.0, penalized * 100.0))))
    return trust_100

