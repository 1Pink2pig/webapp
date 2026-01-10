import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import SessionLocal
from backend.models import User

client = TestClient(app)

# ensure test user exists and override current user dependency
from backend.utils import get_current_user

db = SessionLocal()
user = db.query(User).filter(User.username=='test_api_user').first()
if not user:
    user = User(username='test_api_user', hashed_password='fake', full_name='Test User')
    db.add(user)
    db.commit()
    db.refresh(user)
db.close()

# override dependency
app.dependency_overrides[get_current_user] = lambda: user

# create need
resp = client.post('/api/need/', json={
    'serviceType': '居家维修',
    'title': 'Service Flow Need',
    'description': 'Need for service flow test',
    'imgUrls': [],
    'videoUrl': '',
    'region': '测试区'
})
print('POST need status', resp.status_code, 'json', resp.json())
created = resp.json()
need_id = created.get('id')

# submit service self-recommendation
svc_resp = client.post('/api/service/', json={
    'needId': need_id,
    'serviceType': '居家维修',
    'title': 'I can fix pipes',
    'content': 'Experienced plumber available',
    'files': []
})
print('POST service status', svc_resp.status_code, 'json', svc_resp.json())
svc_created = svc_resp.json()
svc_id = None
if isinstance(svc_created, dict):
    svc_id = svc_created.get('data') or svc_created.get('id')

# fetch service detail
if svc_id:
    detail = client.get(f'/api/service/detail/{svc_id}')
    print('SERVICE DETAIL status', detail.status_code, 'json', detail.json())
else:
    print('Service ID not returned; cannot fetch detail')

