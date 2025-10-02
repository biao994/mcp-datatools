"""
src/mcp_datatools/server.py - 仅提供必须传入 database_url 的工具
"""

from typing import List
from .utils import setup_project_path, database_operation
setup_project_path()

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.logging import get_logger

# 支持相对导入和绝对导入
try:
    from .database import MultiDatabaseManager
except ImportError:
    from mcp_datatools.database import MultiDatabaseManager

from config.settings import config

mcp = FastMCP(config.name)
logger = get_logger(__name__)

def get_database_manager(database_url: str):
    """根据显式指定的数据库URL返回管理器"""
    if not database_url or not isinstance(database_url, str) or not database_url.strip():
        raise ValueError("请提供有效的 database_url")
    return MultiDatabaseManager(database_url.strip())

@mcp.tool(description="获取数据库信息（必须指定 database_url）。例如：get_database_info_by_url('postgresql://user:pass@host:5432/db')")
@database_operation("获取数据库信息")
def get_database_info_by_url(database_url: str) -> str:
    """查询指定数据库的信息（必须传入 database_url）"""
    db_mgr = get_database_manager(database_url)
    info = db_mgr.get_database_info()

    result = "数据库信息:\n"
    result += f"类型: {info.get('type')}\n"
    result += f"连接: {info.get('url')}\n"
    result += f"表数量: {info.get('tables_count')}\n"

    pool = info.get('connection_pool')
    if pool:
        result += "\n连接池状态:\n"
        if 'size' in pool:
            result += f"  池大小: {pool['size']}\n"
        if 'checked_out' in pool:
            result += f"  已连接: {pool['checked_out']}\n"
        if 'checked_in' in pool:
            result += f"  可用连接: {pool['checked_in']}\n"
        if 'overflow' in pool:
            result += f"  溢出连接: {pool['overflow']}\n"

    return result

@mcp.tool(description="列出所有表（必须指定 database_url）。例如：list_tables_by_url('mysql+pymysql://user:pass@host:3306/db')")
@database_operation("获取数据库表列表")
def list_tables_by_url(database_url: str) -> str:
    """查询指定数据库的表列表（必须传入 database_url）"""
    db_mgr = get_database_manager(database_url)
    tables = db_mgr.get_table_names()

    if tables:
        result = f"数据库中共有 {len(tables)} 个表:\n\n"
        for i, table in enumerate(tables, 1):
            result += f"{i}. {table}\n"
        return result
    else:
        return "数据库中没有表"

@mcp.tool(description="获取表结构信息（必须指定 database_url）。例如：schema_info_by_url(['users'], 'sqlite:///path/to.db')")
@database_operation("获取表结构信息")
def schema_info_by_url(table_names: List[str], database_url: str) -> str:
    """获取指定数据库中表的详细结构信息（必须传入 database_url）"""
    if not table_names:
        return "请提供要查询的表名"

    db_mgr = get_database_manager(database_url)
    result_parts = []

    for table_name in table_names:
        try:
            schema_info = db_mgr.get_table_schema(table_name)

            # 格式化表结构信息
            table_section = f"\n{'='*50}\n"
            table_section += f"表名：{table_name}\n"
            table_section += f"列：{schema_info['columns']}\n"
            table_section += f"{'='*50}\n"

            # 列信息
            for col in schema_info['columns']:
                col_type = col['type']
                nullable = "可空" if col['nullable'] else "不可空"
                pk_mark = " 主键" if col['is_primary_key'] else ""
                default_info = f" (默认: {col['default']})" if col['default'] else ""
                table_section += f"  • {col['name']}: {col_type} - {nullable}{pk_mark}{default_info}\n"

            # 主键信息
            if schema_info['primary_keys']:
                table_section += f"\n主键: {', '.join(schema_info['primary_keys'])}\n"

            # 索引信息
            if schema_info['indexes']:
                table_section += "\n索引信息:\n"
                for idx in schema_info['indexes']:
                    unique_mark = "唯一索引" if idx.get('unique', False) else "普通索引"
                    columns = ', '.join(idx['column_names'])
                    table_section += f"  • {idx['name']}: {unique_mark} ({columns})\n"

            # 外键信息
            if schema_info['foreign_keys']:
                table_section += "\n外键关系:\n"
                for fk in schema_info['foreign_keys']:
                    local_cols = ', '.join(fk['constrained_columns'])
                    ref_table = fk['referred_table']
                    ref_cols = ', '.join(fk['referred_columns'])
                    table_section += f"  • {local_cols} → {ref_table}.{ref_cols}\n"

            result_parts.append(table_section)

        except ValueError as e:
            result_parts.append(f"\n表 '{table_name}': {str(e)}\n")
        except Exception as e:
            result_parts.append(f"\n表 '{table_name}' 解析失败: {str(e)}\n")

    return '\n'.join(result_parts)

@mcp.tool(description="执行只读SQL查询（必须指定 database_url；仅支持SELECT，自动加行数限制，支持参数化查询）。例如：execute_query_by_url('SELECT 1', 'postgresql://...')")
@database_operation("执行SQL查询")
def execute_query_by_url(query: str, database_url: str, params: dict = None) -> str:
    """执行只读查询（必须传入 database_url）"""
    if not query or not query.strip():
        return "请提供查询语句"

    db_mgr = get_database_manager(database_url)
    query_params = params if params else None

    result = db_mgr.execute_query(query.strip(), query_params)

    if not result:
        return "查询结果为空"

    result_text = "查询结果:\n"
    for row in result:
        result_text += f"{row}\n"
    return result_text

def main():
    try:
        logger.info(f"启动{config.name} v{config.version}")

        logger.info("当前功能：")
        logger.info("  - get_database_info_by_url(database_url) - 获取数据库信息")
        logger.info("  - list_tables_by_url(database_url) - 获取数据库表列表")
        logger.info("  - schema_info_by_url(table_names, database_url) - 获取表结构")
        logger.info("  - execute_query_by_url(query, database_url, params=None) - 执行SQL只读查询")
        logger.info("MCP服务器启动成功，等待客户端连接...")

        mcp.run()
    except Exception as e:
        logger.error(f"服务器启动失败: {str(e)}")
        raise

if __name__ == "__main__":
    main()