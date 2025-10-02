import os
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.logging import get_logger

from .database import DatabaseManager

from typing import List

mcp = FastMCP("MCP DataTools")
logger = get_logger(__name__)
db_manager = None

def get_database_manager():
    """获取数据库管理器实例"""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager
    
@mcp.tool(description="查询数据库中的所有表")
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


@mcp.tool(description="根据关键词搜索相关的表名。支持模糊匹配，不区分大小写。")
def filter_table_names(keyword: str) -> str:
    """根据关键词搜索相关的表名"""
    try:
        if not keyword or not keyword.strip():
            return "请提供搜索关键词"

        db_mgr = get_database_manager()
        matching_tables = db_mgr.filter_table_names(keyword.strip())
        
        if matching_tables:
            table_list = ", ".join(matching_tables)
            result = f"搜索关键词 '{keyword}' 找到 {len(matching_tables)} 个相关表:\n"
            result += f"匹配的表: {table_list}"
            logger.info(f"关键词 '{keyword}' 匹配到: {table_list}")
            return result
        else:
            all_tables = db_mgr.get_table_names()
            all_table_list = ", ".join(all_tables) if all_tables else "无"
            result = f"搜索关键词 '{keyword}' 没有找到匹配的表。\n"
            result += f"数据库中的所有表: {all_table_list}\n"
            result += f"建议尝试其他关键词，如表名的一部分。"
            logger.info(f"关键词 '{keyword}' 没有找到匹配的表。")
            return result
    except Exception as e:
        error_msg = f"搜索表名失败: {str(e)}"
        logger.error(error_msg)
        return f"{error_msg}"

@mcp.tool(description="获取指定表的详细结构信息，包括列、类型、主键、索引、外键等。支持同时查询多个表。")
def schema_info(table_names: List[str]) -> str:
    """获取指定表的详细结构信息"""
    try:
        if not table_names:
            return "请提供要查询的表名"

        db_mgr = get_database_manager()
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
                column_section = "列信息：\n"
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

        final_result = '\n'.join(result_parts)
        logger.info(f"成功解析 {len(table_names)} 个表的结构")

        return final_result
    except Exception as e:
        error_msg = f"获取表结构信息失败: {str(e)}"
        logger.error(error_msg)
        return f"{error_msg}"

@mcp.tool(description="安全执行SQL查询语句。只支持SELECT查询，自动添加结果限制，支持参数化查询防止SQL注入。")
def execute_query(query: str, params: dict = None) -> str:
    try:
        if not query or not query.strip():
                return "请提供查询语句"
            
        db_mgr = get_database_manager()
        
        # 如果没有提供参数，设为None
        query_params = params if params else None

        # 执行查询
        result = db_mgr.execute_query(query.strip(), query_params)

        if not result:
                return "查询结果为空"
            
        #格式化返结果
        result_text = "查询结果:\n"
        for row in result:
                result_text += f"{row}\n"
                
        return result_text
    
    except ValueError as e:
        # 安全验证失败
        error_msg = f"查询安全验证失败: {str(e)}"
        logger.warning(error_msg)
        return f"{error_msg}\n\n 提示：本工具只支持 SELECT 查询，且会自动添加安全限制。"
        
    except Exception as e:
        error_msg = f"执行查询失败: {str(e)}"
        logger.error(error_msg)
        return f"{error_msg}"


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