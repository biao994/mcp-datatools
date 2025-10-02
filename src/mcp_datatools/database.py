"""
数据库管理模块
"""

import os
from typing import List
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

    def close(self) -> None:
        """关闭数据库连接"""
        if self.engine:
            self.engine.dispose()
            logger.info("数据库连接已关闭")
        