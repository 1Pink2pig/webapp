#!/usr/bin/env python3
"""
Create an admin user in the project's SQLite database.
Usage:
  python create_admin.py                       # creates admin/admin123
  python create_admin.py --username foo --password secret --email a@b.c --full-name 管理员

The script uses the project's `backend` package to access models and hashing function.
"""
import argparse
import sys
from datetime import datetime

# ensure project root is on sys.path so `backend` imports work
import os
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.database import SessionLocal
from backend.models import User
from backend.utils import get_password_hash


def main():
    p = argparse.ArgumentParser(description="Create admin user in haofuwu.db")
    p.add_argument('--username', '-u', default='admin', help='username (default: admin)')
    p.add_argument('--password', '-p', default='admin123', help='password (default: admin123)')
    p.add_argument('--email', '-e', default='admin@example.com', help='email')
    p.add_argument('--full-name', '-f', default='管理员', help='full name')
    p.add_argument('--phone', default='', help='phone')
    args = p.parse_args()

    username = args.username
    password = args.password
    email = args.email
    full_name = args.full_name
    phone = args.phone

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            print(f"⚠️  User with username '{username}' already exists (id={existing.id}). No changes made.")
            return

        hashed = get_password_hash(password)
        user = User(
            username=username,
            email=email,
            hashed_password=hashed,
            full_name=full_name,
            phone=phone,
            user_type='系统管理员',
            register_time=datetime.utcnow(),
            update_time=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"✅ Created admin user: id={user.id}, username={user.username}, email={user.email}")
    except Exception as e:
        db.rollback()
        print(f"❌ Failed to create admin user: {e}")
        raise
    finally:
        db.close()


if __name__ == '__main__':
    main()
