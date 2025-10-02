"""
src/mcp_datatools/utils.py - 公共工具函数
"""

import os
import sys
from typing import Any, Callable
from functools import wraps
from mcp.server.fastmcp.utilities.logging import get_logger

logger = get_logger(__name__)

def setup_project_path():
    """统一的项目路径设置"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 从 src/mcp_datatools 到项目根目录
    project_root = os.path.dirname(os.path.dirname(current_dir))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

def handle_database_error(operation: str, error: Exception) -> str:
    """统一的数据库错误处理"""
    error_msg = f"{operation}失败: {str(error)}"
    logger.error(error_msg)
    return error_msg

def database_operation(operation_name: str):
    """数据库操作装饰器，统一错误处理"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                result = func(*args, **kwargs)
                logger.info(f"成功{operation_name}")
                return result
            except Exception as e:
                return handle_database_error(operation_name, e)
        return wrapper
    return decorator

def mask_password(url: str) -> str:
    """隐藏URL中的密码"""
    if "@" in url and "://" in url:
        parts = url.split("://")
        if len(parts) == 2:
            protocol = parts[0]
            rest = parts[1]
            if "@" in rest:
                user_pass, host_db = rest.split("@", 1)
                if ":" in user_pass:
                    user, _ = user_pass.split(":", 1)
                    return f"{protocol}://{user}:***@{host_db}"
    return url
