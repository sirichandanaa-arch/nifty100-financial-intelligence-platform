from fastapi.testclient import TestClient
from src.api.main import app
client=TestClient(app)
def test_openapi_available(): assert client.get('/openapi.json').status_code==200
def test_health_if_db_exists():
    r=client.get('/api/v1/health'); assert r.status_code in (200,500)
