from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

# try multiple test ids
for test_id in [1, 'service_1', '99999', 'abc']:
    try:
        resp = client.get(f"/api/service/detail/{test_id}")
        print('---')
        print('request id ->', test_id)
        print('status_code ->', resp.status_code)
        try:
            print('json ->', resp.json())
        except Exception as e:
            print('failed to parse json:', e)
    except Exception as e:
        print('error calling API for id', test_id, '->', e)

