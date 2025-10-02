"""
config/settings.py - 应用配置管理
"""
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
from typing import Dict, Any

class DatabaseConfig(BaseSettings):
    """数据库配置"""
    model_config = ConfigDict(env_prefix="DB_")
    
    pool_size : int = Field(default=20, description="连接池大小")
    max_overflow: int = Field(default=10, description="连接池最大溢出数")
    pool_timeout: int = Field(default=30, description="连接池超时时间")
    pool_recycle: int = Field(default=3600, description="连接池回收时间")
    echo: bool = Field(default=False, description="是否打印SQL语句")

class AppConfig(BaseSettings):
    """应用配置"""
    model_config = ConfigDict(env_prefix="APP_")
    
    name: str = Field(default="MCP DataTools", description="应用名称")
    version: str = Field(default="1.0.0", description="应用版本")
    log_level: str = Field(default="INFO", description="日志级别")
    max_query_results: int = Field(default=1000, description="结果最大查询行数")

    # 数据库配置
    database: DatabaseConfig = Field(default_factory=DatabaseConfig, description="数据库配置")

# 全局配置实例
config = AppConfig()