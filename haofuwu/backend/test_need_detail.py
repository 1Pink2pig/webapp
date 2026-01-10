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
from backend.utils import get_current_user as orig_get_current_user

app.dependency_overrides[get_current_user] = lambda: user

# create need
resp = client.post('/api/need/', json={
    'serviceType': '居家维修',
    'title': 'Detail Test Need',
    'description': 'Detail test',
    'imgUrls': [],
    'videoUrl': '',
    'region': '测试区'
})
print('POST status', resp.status_code, 'json', resp.json())
created = resp.json()
need_id = created.get('id')

# call detail
resp2 = client.get(f'/api/need/detail/{need_id}')
print('DETAIL status', resp2.status_code)
print('DETAIL json', resp2.json())

