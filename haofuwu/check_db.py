import sqlite3
import os

db_path = "haofuwu.db"

# 检查文件是否存在
if os.path.exists(db_path):
    print(f"✅ 数据库文件存在: {os.path.abspath(db_path)}")
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查看所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    if tables:
        print("✅ 已创建的表:")
        for table in tables:
            table_name = table[0]
            print(f"\n{'='*60}")
            print(f"表名: {table_name}")
            print(f"{'='*60}")
            
            # 查看表结构
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            print("表结构 (列名 | 数据类型 | 是否可空 | 是否主键):")
            print("-" * 60)
            
            # 首先获取列名，用于后续显示数据
            col_names = []
            for col in columns:
                col_id, name, type_, notnull, pk, default = col
                col_names.append(name)
                notnull_text = "NOT NULL" if notnull else "NULL"
                pk_text = "PRIMARY KEY" if pk else ""
                default_text = f"默认值: {default}" if default else ""
                print(f"  {name:<15} {type_:<10} {notnull_text:<10} {pk_text}")
            
            # 查看表数据
            print(f"\n表数据:")
            print("-" * 60)
            
            # 首先获取数据
            cursor.execute(f"SELECT * FROM {table_name};")
            rows = cursor.fetchall()
            
            if rows:
                # 打印表头
                print(" | ".join(col_names))
                print("-" * (len(col_names) * 15))
                
                # 打印数据（最多显示20行）
                max_rows_to_show = 20
                for i, row in enumerate(rows[:max_rows_to_show]):
                    # 格式化每行数据
                    formatted_row = []
                    for value in row:
                        if value is None:
                            formatted_row.append("NULL")
                        elif isinstance(value, str):
                            # 如果字符串太长，截断显示
                            if len(value) > 20:
                                formatted_row.append(value[:17] + "...")
                            else:
                                formatted_row.append(value)
                        else:
                            formatted_row.append(str(value))
                    
                    print(" | ".join(formatted_row))
                
                # 显示总行数信息
                total_rows = len(rows)
                if total_rows > max_rows_to_show:
                    print(f"... 还有 {total_rows - max_rows_to_show} 行未显示")
                print(f"\n总行数: {total_rows}")
                
                # 显示数据预览信息
                print(f"\n数据预览:")
                print(f"第一行: {rows[0]}")
                print(f"最后一行: {rows[-1]}")
            else:
                print("表中没有数据")
    else:
        print("❌ 数据库中没有表")
    
    conn.close()
else:
    print(f"❌ 数据库文件不存在: {os.path.abspath(db_path)}")
    print("检查当前目录:", os.getcwd())