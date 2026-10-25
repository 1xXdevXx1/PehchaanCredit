def make_lender_decision(credit_score: int, svps: float, rating: str, flags: list) -> dict:
    # Lender decision engine considering score, fraud risk, and anomaly flags
    if svps >= 0.25 or 'CIRCULAR_LOOP' in flags or 'SEVERE_FRAUD' in flags:
        decision = 'REVIEW'
        action = 'Review flagged transactions'
        confidence = 'Medium'
        desc = 'Suspicious-volume patterns or cyclical transfers detected. Underwriter review recommended.'
    elif credit_score >= 750 and svps < 0.12:
        decision = 'STRONG_APPROVAL'
        action = 'Proceed to instant sanction'
        confidence = 'High'
        desc = 'Strong behavioral evidence with low fraud exposure. Vendor exhibits healthy operating rhythm.'
    elif credit_score >= 680 and svps < 0.18:
        decision = 'APPROVAL'
        action = 'Proceed to standard sanction'
        confidence = 'High'
        desc = 'Consistent business activity meeting behavioral credit thresholds.'
    elif credit_score >= 600:
        decision = 'REVIEW'
        action = 'Request additional supplier receipts'
        confidence = 'Medium'
        desc = 'Moderate performance. Additional collateral or vendor verification advisable.'
    else:
        decision = 'HIGH_RISK'
        action = 'Decline or require guarantor'
        confidence = 'High'
        desc = 'Elevated default probability and weak behavioral signals observed.'
        
    return {
        'decision': decision,
        'action': action,
        'confidence': confidence,
        'recommendation_text': desc
    }
