import os
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.logging import get_logger

from .database import DatabaseManager


mcp = FastMCP("MCP DataTools")
logger = get_logger(__name__)
db_manager = None

def get_database_manager():
    """获取数据库管理器实例"""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager
    
@mcp.tool()
def list_tables() -> str:
    """获取数据库表列表"""
    try:
        db_mgr = get_database_manager()
        tables = db_mgr.get_table_names()
        
        if tables:
            table_list = ",".join(tables)
            result = f"数据库中共有 {len(tables)} 个表:\n\n"
            for i,table in enumerate(tables,1):
                result += f"{i}. {table}\n"
            logger.info(f"成功返回 {len(tables)} 个表: {table_list}")
            return result
        else:
            return "数据库中没有表"

    except Exception as e:
        error_msg = f"获取数据库表列表失败: {str(e)}"
        logger.error(error_msg)
        return f"{error_msg}\n\n请检查数据库连接。"
        

def main():
    try:
        logger.info("启动MCP DataTools服务器")

        db_mgr = get_database_manager()

        if db_mgr.test_connection():
            logger.info("数据库连接测试成功")
        else:
            logger.warning("数据库连接测试失败，但服务器仍会启动")
            logger.info("提示：运行 'python data/create_test_db.py' 创建测试数据库")

        logger.info("当前功能：list_tables() - 获取数据库表列表")
        logger.info("MCP服务器启动成功，等待客户端连接...")
        
        mcp.run()

    except Exception as e:
        logger.error(f"服务器启动失败: {str(e)}")
        raise

if __name__ == "__main__":
    main()