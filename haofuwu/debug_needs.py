import sqlite3

DB = 'D:/WebFinal/haofuwu/haofuwu.db'
conn = sqlite3.connect(DB)
cur = conn.cursor()

print('PRAGMA table_info(needs):')
cur.execute("PRAGMA table_info(needs);")
for row in cur.fetchall():
    print(row)

print('\nUsers:')
cur.execute('SELECT id, username FROM users ORDER BY id')
for r in cur.fetchall():
    print(r)

print('\nNeeds:')
# Show explicit columns
cur.execute('SELECT id, title, service_type, owner_id, create_time, update_time FROM needs ORDER BY id')
rows = cur.fetchall()
for r in rows:
    print(r)

conn.close()

