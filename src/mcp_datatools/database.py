"""
数据库管理模块
"""

import os
from typing import List, Dict, Any
from contextlib import contextmanager
from sqlalchemy import create_engine,inspect,text
from sqlalchemy.exc import SQLAlchemyError
from mcp.server.fastmcp.utilities.logging import get_logger



logger = get_logger(__name__)

class DatabaseManager:
    """数据库管理器"""
    def __init__(self):
        """初始化数据库管理器"""
        
        self.database_url = os.getenv("DB_URL")
        self.engine = None
        self._connect()


    def _connect(self) -> None:
        """连接数据库"""
        try:
            self.engine = create_engine(self.database_url, echo=False)
            logger.info(f"成功连接到数据库: {self.database_url}")
        except Exception as e:
            logger.error(f"连接数据库时出错: {str(e)}")
            raise

    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        if not self.engine:
            raise RuntimeError("数据库未连接")
        
        conn = self.engine.connect()
        try:
            yield conn
        finally:
            conn.close()
    
    def get_table_names(self) -> List[str]:
        """获取数据库中的所有表名"""
        try:
            with self.get_connection() as conn:
                inspector = inspect(conn)
                table_names = inspector.get_table_names()
                return table_names
        except SQLAlchemyError as e:
            logger.error(f"获取表名失败: {e}")
            raise

    def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            with self.get_connection() as conn:

                result = conn.execute(text("SELECT 1")).scalar()
                return result == 1
        except Exception as e:
            logger.error(f"测试数据库连接时出错: {str(e)}")
            return False


    def get_db_info(self) -> str:
        try:
            tables = self.get_table_names()
            return f"数据库URL: {self.database_url}\n共有 {len(tables)} 个表"
        except Exception:
            return f"数据库URL: {self.database_url}\n数据库连接失败"

    def filter_table_names(self, keyword: str) -> List[str]:
        """根据关键词搜索相关表名"""
        try:
            all_tables = self.get_table_names()
            matching_tables = [table for table in all_tables if keyword.lower() in table.lower()]
            return matching_tables
        except Exception as e:
            logger.error(f"搜索表名失败: {e}")
            raise

    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """获取指定表的详细结构信息"""
        try:
            with self.get_connection() as conn:
                inspector = inspect(conn)

                # 验证表是否存在
                if table_name not in inspector.get_table_names():
                    raise ValueError(f"表 '{table_name}' 不存在")
                
                # 获取列信息
                columns = inspector.get_columns(table_name)
                
                # 获取主键信息
                pk_constraint = inspector.get_pk_constraint(table_name)
                primary_keys = set(pk_constraint["constrained_columns"])
                           
                # 获取索引信息
                indexes = inspector.get_indexes(table_name)
                
                # 获取外键信息
                foreign_keys = inspector.get_foreign_keys(table_name)

                # 格式化列信息
                formatted_columns = []
                for col in columns:
                    col_info = {
                        "name": col["name"],
                        "type": str(col["type"]),
                        "nullable": col["nullable"],
                        "default": col.get("default"),
                        "is_primary_key": col["name"] in primary_keys
                    }
                    formatted_columns.append(col_info)

                schema_info = {
                    "table_name": table_name,
                    "columns": formatted_columns,
                    "primary_keys": list(primary_keys),
                    "indexes": indexes,
                    "foreign_keys": foreign_keys,
                    "column_count": len(columns)
                }

                return schema_info
        except Exception as e:
            logger.error(f"获取表结构信息失败: {e}")
            raise

    def _validate_query(self, query: str) -> None:
        """验证查询安全性"""
        query_upper = query.upper().strip()

        # 检查危险的SQL操作
        dangerous_keywords = [
            "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", "TRUNCATE"
        ]

        for keyword in dangerous_keywords:
            if keyword in query_upper:
                raise ValueError(f"查询包含危险操作: {keyword}")
        
        # 检查是否是SELECT查询
        if not query_upper.startswith("SELECT"):
            raise ValueError("只允许执行SELECT查询")
    
    def _add_limit_to_query(self, query: str, limit: int) -> str:
        """为查询添加LIMIT子句"""
        query_upper = query.upper()
        
        # 如果已经有LIMIT，不再添加
        if "LIMIT" in query_upper:
            return query
    
        # 添加LIMIT子句
        return f"{query.rstrip(';')} LIMIT {limit}"
    
    def execute_query(self, query: str, params: dict =None) -> List[Dict[str, Any]]:
        """安全执行查询"""
        try:
            # 验证查询安全性
            self._validate_query(query)
            
            # 添加默认限制
            limited_query = self._add_limit_to_query(query, 1000)

            with self.get_connection() as conn:
                if params:
                    # 使用参数化查询
                    result = conn.execute(text(limited_query), params)
                else:
                    result = conn.execute(text(limited_query))
                
                # 获取列名
                columns = result.keys()
                rows = []
                for row in result:
                    row_dict = dict(zip(columns, row))
                    rows.append(row_dict)
                
                return rows

        except Exception as e:
            logger.error(f"执行查询失败: {e}")
            raise

    def close(self) -> None:
        """关闭数据库连接"""
        if self.engine:
            self.engine.dispose()
            logger.info("数据库连接已关闭")
        