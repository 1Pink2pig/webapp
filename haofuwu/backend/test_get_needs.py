import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

print('GET /api/need/')
resp = client.get('/api/need/')
print('Status code:', resp.status_code)
try:
    print('Response JSON:', resp.json())
except Exception as e:
    print('Response text:', resp.text)

