from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.database import init_db
from backend.app.routers.vendors import router as vendors_router
from backend.ml.advanced_tft import get_advanced_tft_status
from backend.ml.advanced_tgat import get_advanced_tgat_status

app = FastAPI(
    title='PehchaanCredit API — Behavioral Trust Engine',
    description='AI-Based Behavioral Trust Engine for Credit Assessment of Street Vendors Using Digital Transaction Data',
    version='1.0.0'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.on_event('startup')
def on_startup():
    init_db()

@app.get('/health', tags=['system'])
def health_check():
    return {
        'status': 'ok',
        'engine': 'PehchaanCredit Behavioral Trust Engine',
        'version': '1.0.0',
        'disclaimer': 'Prototype score for demonstration. Not an official RBI or CIBIL bureau rating.'
    }

@app.get('/api/model-status', tags=['ml'])
def get_model_status():
    return {
        'xgboost': {'status': 'TRAINED', 'role': 'Base credit quality estimation (Q_base)'},
        'isolation_forest': {'status': 'IMPLEMENTED', 'role': 'Behavioral anomaly detection'},
        'networkx_graph': {'status': 'IMPLEMENTED', 'role': 'Circular fund flow and reciprocity detection'},
        'stl_decomposition': {'status': 'IMPLEMENTED', 'role': 'Seasonality and resilience analysis'},
        'shap': {'status': 'IMPLEMENTED', 'role': 'Human-readable factor explainability'},
        'tgat_time2vec': get_advanced_tgat_status(),
        'tft': get_advanced_tft_status()
    }

app.include_router(vendors_router)
