import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get('/health')
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'ok';

def test_model_status():
    response = client.get('/api/model-status')
    assert response.status_code == 200
    data = response.json()
    assert data['xgboost']['status'] == 'TRAINED';
    assert data['tft']['status'] == 'OPTIONAL/NOT_TRAINED';

def test_get_vendors():
    response = client.get('/api/vendors')
    assert response.status_code == 200
    vendors = response.json()
    assert len(vendors) > 0
    assert 'credit_score' in vendors[0]

def test_get_vendor_assessment():
    response = client.get('/api/vendors/VND-1000/assessment')
    assert response.status_code == 200
    asm = response.json()
    assert 300 <= asm['credit_score'] <= 900
    assert 'decision' in asm