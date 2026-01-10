from backend.database import SessionLocal
from backend import crud, models
from sqlalchemy.orm import Session

def ensure_user(db: Session, username):
    u = db.query(models.User).filter(models.User.username == username).first()
    if u:
        return u
    # create a simple user with hashed_password set to dummy
    u = models.User(username=username, hashed_password='x', full_name=username)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def main():
    db = SessionLocal()
    try:
        # ensure two users
        u1 = ensure_user(db, 'test_user_1')
        u2 = ensure_user(db, 'test_user_2')
        print('Users:', u1.id, u1.username, ' ; ', u2.id, u2.username)

        # create a need for user1
        class DummyNeedIn:
            def __init__(self, title):
                self.title = title
                self.serviceType = '居家维修'
                self.region = '北京市'
                self.description = '测试需求'
                self.imgUrls = []
                self.videoUrl = ''

        need_in = DummyNeedIn('Test Need For Flow')
        n = crud.create_need(db, u1.id, need_in)
        print('Created need id=', n.id)

        # list user1 needs before any service
        needs_before = crud.get_needs_my_list(db, u1.id)
        print('Needs before count:', len(needs_before), 'ids:', [x.id for x in needs_before])

        # create service by user2 for that need
        class DummyServiceIn:
            def __init__(self):
                self.title = 'I can help'
                self.content = 'I will help'
                self.serviceType = '居家维修'
                self.files = []
                self.needId = n.id

        svc_in = DummyServiceIn()
        s = crud.create_service(db, u2.id, svc_in)
        print('Created service id=', s.id, 'for need=', s.need_id)

        # list user1 needs after service created
        needs_after = crud.get_needs_my_list(db, u1.id)
        print('Needs after count:', len(needs_after), 'ids:', [x.id for x in needs_after])
        for item in needs_after:
            print('need', item.id, 'hasResponse=', item.hasResponse)

    finally:
        db.close()

if __name__ == '__main__':
    main()

