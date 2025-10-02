"""
创建测试数据库
"""

import sqlite3
import os
from pathlib import Path

def create_simple_test_database():
    """创建简单测试数据库"""
    
    data_dir = Path(__file__).parent.parent / "data"
    db_path = data_dir / "test.db"
    
    print(" 测试数据库创建器")
    print(f"数据库路径: {db_path}")
    
    if db_path.exists():
        os.remove(db_path)
        print("删除旧数据库文件")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("创建基础表结构...")
        
        # 创建用户表
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                email VARCHAR(100) NOT NULL
            )
        """)
        
        # 创建产品表
        cursor.execute("""
            CREATE TABLE products (
                id INTEGER PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                price DECIMAL(10, 2) NOT NULL
            )
        """)
        
        # 创建订单表
        cursor.execute("""
            CREATE TABLE orders (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                total_amount DECIMAL(10, 2)
            )
        """)
        
        print("插入测试数据...")
        
        # 插入测试数据
        cursor.execute("INSERT INTO users (name, email) VALUES ('Alice', 'alice@test.com')")
        cursor.execute("INSERT INTO users (name, email) VALUES ('Bob', 'bob@test.com')")
        
        cursor.execute("INSERT INTO products (name, price) VALUES ('笔记本电脑', 5999.99)")
        cursor.execute("INSERT INTO products (name, price) VALUES ('鼠标', 129.99)")
        
        cursor.execute("INSERT INTO orders (user_id, total_amount) VALUES (1, 6129.98)")
        cursor.execute("INSERT INTO orders (user_id, total_amount) VALUES (2, 129.99)")
        
        conn.commit()
        
        print("测试数据库创建成功！")
        print("数据库包含表:")
        print("  1. users - 用户表 (2条记录)")
        print("  2. products - 产品表 (2条记录)")
        print("  3. orders - 订单表 (2条记录)")
        
    except Exception as e:
        print(f"创建数据库时出错: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    create_simple_test_database()