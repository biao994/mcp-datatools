"""
src/mcp_datatools/database.py - 多数据库管理器
"""

from .utils import setup_project_path
setup_project_path()

from typing import List, Dict, Any
from contextlib import contextmanager
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import QueuePool
from mcp.server.fastmcp.utilities.logging import get_logger

from config.settings import config
from .utils import mask_password

logger = get_logger(__name__)

class MultiDatabaseManager:
    """多数据库管理器"""
    
    def __init__(self, database_url: str):
        """初始化数据库管理器（必须显式提供 database_url）"""
        if not database_url or not isinstance(database_url, str) or not database_url.strip():
            raise ValueError("必须显式提供 database_url")
        self.database_url = database_url.strip()
        self.engine = None
        self.db_type = self._detect_database_type()
        self._connect()
    
    def _detect_database_type(self) -> str:
        """检测数据库类型"""
        url = self.database_url.lower()
        if url.startswith("postgresql://") or url.startswith("postgres://"):
            return "postgresql"
        elif url.startswith("mysql://") or url.startswith("mysql+"):
            return "mysql"
        elif url.startswith("sqlite://"):
            return "sqlite"
        else:
            return "unknown"
    
    def _connect(self) -> None:
        """连接数据库"""
        try:
            # 根据数据库类型调整配置
            if self.db_type == "sqlite":
                # SQLite使用最简配置，避免复杂的连接池
                self.engine = create_engine(
                    self.database_url,
                    echo=config.database.echo,
                    connect_args={"check_same_thread": False}  # 允许多线程
                )
            else:
                # PostgreSQL和MySQL使用完整连接池配置
                self.engine = create_engine(
                    self.database_url,
                    poolclass=QueuePool,  # 明确指定队列式连接池
                    pool_size=config.database.pool_size,
                    max_overflow=config.database.max_overflow,
                    pool_timeout=config.database.pool_timeout,
                    pool_recycle=config.database.pool_recycle,
                    echo=config.database.echo
                )
                        
            logger.info(f"成功连接到 {self.db_type} 数据库: {mask_password(self.database_url)}")
            
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
    
    def get_database_info(self) -> Dict[str, Any]:
        """获取数据库信息"""
        try:
            with self.get_connection() as conn:
                info = {
                    "type": self.db_type,
                    "url": mask_password(self.database_url),
                    "tables_count": len(self.get_table_names()),
                }
                
                # 只为非SQLite数据库显示连接池信息
                if self.db_type != "sqlite":
                    if hasattr(self.engine, 'pool'):
                        try:
                            pool_info = {}
                            # 统一尝试获取各种连接池信息
                            if hasattr(self.engine.pool, 'size'):
                                pool_info["size"] = self.engine.pool.size()
                            if hasattr(self.engine.pool, 'checkedout'):
                                pool_info["checked_out"] = self.engine.pool.checkedout()
                            if hasattr(self.engine.pool, 'overflow'):
                                pool_info["overflow"] = self.engine.pool.overflow()
                            # 对于checked_in，不同的连接池实现可能不同
                            if hasattr(self.engine.pool, 'checked_in'):
                                pool_info["checked_in"] = self.engine.pool.checked_in()
                            elif hasattr(self.engine.pool, 'checkedin'):
                                pool_info["checked_in"] = self.engine.pool.checkedin()
                            else:
                                # 如果都没有，计算可用连接数
                                if "size" in pool_info and "checked_out" in pool_info:
                                    pool_info["checked_in"] = pool_info["size"] - pool_info["checked_out"]
                            
                            info["connection_pool"] = pool_info if pool_info else None
                        except Exception as pool_error:
                            logger.warning(f"获取连接池信息失败: {pool_error}")
                            info["connection_pool"] = None
                    else:
                        info["connection_pool"] = None
                else:
                    # SQLite 不显示连接池信息
                    info["connection_pool"] = None
                
                return info
        except Exception as e:
            logger.error(f"获取数据库信息失败: {e}")
            return {"type": self.db_type, "error": str(e)}
    
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
    
    def filter_table_names(self, keyword: str) -> List[str]:
        """根据关键词搜索相关表名"""
        try:
            all_tables = self.get_table_names()
            matching_tables = [
                table for table in all_tables 
                if keyword.lower() in table.lower()
            ]
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
    
    def execute_query(self, query: str, params: dict = None) -> List[Dict[str, Any]]:
        """安全执行SQL查询"""
        try:
            # 验证查询安全性
            self._validate_query(query)
            
            # 添加默认限制
            limited_query = self._add_limit_to_query(query, config.max_query_results)
            
            with self.get_connection() as conn:
                if params:
                    # 使用参数化查询
                    result = conn.execute(text(limited_query), params)
                else:
                    # 直接执行查询
                    result = conn.execute(text(limited_query))
                
                # 获取列名
                columns = result.keys()
                
                # 转换为字典列表
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