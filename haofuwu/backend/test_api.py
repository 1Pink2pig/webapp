import sys, os
# ensure the repository root (parent of backend/) is on sys.path so `import backend.*` works
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
# use absolute imports referencing the backend package
from backend.main import app
from backend.database import get_db, engine, SessionLocal
from sqlalchemy.orm import Session
from backend.utils import get_current_user
from backend.models import User

# create a client
client = TestClient(app)

# create or get a test user


def ensure_test_user():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == 'test_api_user').first()
        if not user:
            user = User(username='test_api_user', hashed_password='fake', full_name='Test User')
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    finally:
        db.close()

TEST_USER = ensure_test_user()

# override dependency
def fake_current_user():
    return TEST_USER

app.dependency_overrides[get_current_user] = fake_current_user

print('Posting to /api/need/')
resp = client.post('/api/need/', json={
    'serviceType': '居家维修',
    'title': 'Test Need from script',
    'description': 'This is a test need',
    'imgUrls': [],
    'videoUrl': '',
    'region': '测试区'
})
print('Status code:', resp.status_code)
try:
    print('Response JSON:', resp.json())
except Exception as e:
    print('Response text:', resp.text)
