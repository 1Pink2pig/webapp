import sqlite3
DB = 'D:/WebFinal/haofuwu/haofuwu.db'
conn = sqlite3.connect(DB)
cur = conn.cursor()
print('PRAGMA table_info(services):')
cur.execute("PRAGMA table_info(services);")
for row in cur.fetchall():
    print(row)
print('\nServices rows:')
cur.execute('SELECT id, title, need_id, owner_id, status, create_time FROM services ORDER BY id')
for r in cur.fetchall():
    print(r)
conn.close()

