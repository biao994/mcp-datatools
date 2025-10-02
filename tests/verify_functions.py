"""
tests/verify_functions.py - 功能验证脚本
"""

import os
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

def verify_database_connection():
    """验证数据库连接"""
    print("=== 数据库连接验证 ===")
    
    # 设置数据库URL
    db_path = project_root / "data" / "test.db"
    if not db_path.exists():
        print("测试数据库不存在！")
        return False
    
    os.environ['DB_URL'] = f'sqlite:///{db_path}'
    
    try:
        from mcp_datatools.database import DatabaseManager
        db_mgr = DatabaseManager()
        
        if db_mgr.test_connection():
            print("数据库连接成功")
            return True
        else:
            print("数据库连接失败")
            return False
    except Exception as e:
        print(f"数据库连接错误: {e}")
        return False

def verify_basic_functions():
    """验证基础功能"""
    print("\n=== 基础功能验证 ===")
    
    try:
        from mcp_datatools.database import DatabaseManager
        db_mgr = DatabaseManager()
        
        # 测试1: 获取表名
        print("1. 测试 list_tables() 功能...")
        tables = db_mgr.get_table_names()
        print(f"   找到 {len(tables)} 个表: {', '.join(tables)}")
        
        # 测试2: 搜索表名
        print("2. 测试 filter_table_names() 功能...")
        user_tables = db_mgr.filter_table_names('user')
        print(f"   搜索 'user' 找到: {user_tables}")
        
        # 测试3: 获取表结构
        print("3. 测试 get_table_schema() 功能...")
        if tables:
            schema = db_mgr.get_table_schema(tables[0])
            print(f"  表 '{tables[0]}' 有 {schema['column_count']} 个列")
        
        # 测试4: 执行查询
        print("4. 测试 execute_query() 功能...")
        result = db_mgr.execute_query("SELECT COUNT(*) as count FROM users")
        print(f"   查询结果: {result}")
        
        return True
        
    except Exception as e:
        print(f"功能验证失败: {e}")
        return False

def main():
    """主验证流程"""
    print("MCP DataTools 功能验证")
    print("=" * 50)
    
    # 验证数据库连接
    db_ok = verify_database_connection()
    
    if db_ok:
        # 验证基础功能
        func_ok = verify_basic_functions()
        
        if func_ok:
            print("\n 所有基础功能验证通过！")
        else:
            print("\n部分功能验证失败，请检查代码")
    else:
        print("\n数据库连接失败，请先创建测试数据库")
    
    print("\n" + "=" * 50)
    print("验证完成！现在可以在Cursor中测试MCP功能了。")

if __name__ == "__main__":
    main()