"""Create admin user script for haofuwu project.

Usage:
  python create_admin_user.py

This script will:
- connect to the project's SQLite database via backend.database.SessionLocal
- check if a user named 'admin' exists; if yes, exit reporting existing user
- otherwise create a user with username 'admin', password 'admin123', and set user_type to '系统管理员'
"""

from backend.database import SessionLocal
from backend import crud, models
from backend.utils import get_password_hash
import datetime

USERNAME = 'admin'
PASSWORD = 'admin123'


def main():
    db = SessionLocal()
    try:
        existing = crud.get_user_by_username(db, USERNAME)
        if existing:
            print(f"Admin user already exists: id={existing.id}, username={existing.username}")
            return

        # create models.User instance directly to set user_type
        now = datetime.datetime.utcnow()
        hashed = get_password_hash(PASSWORD)
        user = models.User(
            username=USERNAME,
            email=None,
            hashed_password=hashed,
            full_name='系统管理员',
            phone=None,
            user_type='系统管理员',
            register_time=now,
            update_time=now
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Created admin user: id={user.id}, username={user.username}")
    finally:
        db.close()

if __name__ == '__main__':
    main()

