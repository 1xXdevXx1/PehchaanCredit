def get_advanced_tft_status() -> dict:
    return {
        'model_name': 'Temporal Fusion Transformer (TFT)',
        'status': 'OPTIONAL/NOT_TRAINED',
        'is_trained': False,
        'description': 'Modular interface for longitudinal multi-horizon forecasting. Live scoring utilizes trained XGBoost baseline with TreeSHAP explanations.'
    }
