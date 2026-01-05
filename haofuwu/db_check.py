import sqlite3
db='d:/WebApp/haofuwu/haofuwu/haofuwu.db'
c=sqlite3.connect(db); cur=c.cursor()
print(cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall())
print(cur.execute("SELECT * FROM users").fetchall())
c.close()