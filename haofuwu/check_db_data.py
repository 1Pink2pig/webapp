#!/usr/bin/env python3
"""
Lightweight DB data checker for haofuwu.db
Usage:
  python check_db_data.py                # checks ./haofuwu.db
  python check_db_data.py --db path/to/db

Prints table row counts and a final summary (whether any table contains rows).
"""
import argparse
import sqlite3
import os
import sys


def get_tables(conn):
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    return [r[0] for r in cur.fetchall()]


def count_rows(conn, table_name):
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT COUNT(*) FROM '{table_name}'")
        return cur.fetchone()[0]
    except Exception:
        # If counting fails (e.g. table name oddities), return None to indicate unknown
        return None


def main():
    p = argparse.ArgumentParser(description='Check SQLite DB for presence of data (row counts per table)')
    p.add_argument('--db', '-d', default='haofuwu.db', help='Path to SQLite database file (default: haofuwu.db)')
    args = p.parse_args()

    db_path = args.db
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {os.path.abspath(db_path)}")
        sys.exit(2)

    try:
        conn = sqlite3.connect(db_path)
    except Exception as e:
        print(f"❌ Failed to open database: {e}")
        sys.exit(3)

    try:
        tables = get_tables(conn)
    except Exception as e:
        print(f"❌ Failed to list tables: {e}")
        conn.close()
        sys.exit(4)

    if not tables:
        print(f"⚠️  No user tables found in database: {os.path.abspath(db_path)}")
        conn.close()
        sys.exit(0)

    total_rows = 0
    any_data = False

    print(f"Database: {os.path.abspath(db_path)}")
    print(f"Found {len(tables)} table(s):\n")

    for t in tables:
        cnt = count_rows(conn, t)
        if cnt is None:
            print(f" - {t}: could not count rows")
        else:
            print(f" - {t}: {cnt} row(s)")
            total_rows += cnt
            if cnt > 0:
                any_data = True

    print("\n" + ("✅ Database has data" if any_data else "❌ No data found in any table"))
    print(f"Total rows across all tables: {total_rows}")

    conn.close()

    # exit code 0 always for informational run; non-zero used above for file/error conditions


if __name__ == '__main__':
    main()

