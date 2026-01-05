import sqlite3

# 连接数据库
conn = sqlite3.connect('haofuwu.db')
cursor = conn.cursor()

print("=== 用户表数据 ===")
cursor.execute("SELECT * FROM users;")
users = cursor.fetchall()
if users:
    for user in users:
        print(f"ID: {user[0]}, 用户名: {user[1]}, 邮箱: {user[2]}, 姓名: {user[4]}")
else:
    print("用户表为空")

print("\n=== 需求表数据 ===")
cursor.execute("SELECT * FROM needs;")
needs = cursor.fetchall()
if needs:
    for need in needs:
        print(f"ID: {need[0]}, 标题: {need[1]}, 所有者ID: {need[3]}, 创建时间: {need[4]}")
else:
    print("需求表为空")

print("\n=== 服务表数据 ===")
cursor.execute("SELECT * FROM services;")
services = cursor.fetchall()
if services:
    for service in services:
        print(f"ID: {service[0]}, 标题: {service[1]}, 所有者ID: {service[3]}, 状态: {service[5]}")
else:
    print("服务表为空")

conn.close()