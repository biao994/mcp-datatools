# MCP DataTools

一个基于MCP协议的数据库智能助手，让AI能够安全地连接和操作数据库。

## 🎯 项目概述

MCP DataTools是一个基于Model Context Protocol (MCP)的数据库工具，它让AI助手能够安全地连接和操作数据库。通过MCP协议，AI可以调用预设的数据库工具函数，实现智能的数据库查询和分析。

> 📝 本项目有详细的开发教程博客，欢迎阅读：[从零开始：MCP数据库助手](https://blog.csdn.net/weixin_46253270/category_13058724.html?spm=1001.2014.3001.5482)

## ✨ 核心功能

### v2.0.0 功能特性
- 🔍 **list_tables()** - 获取数据库表列表
- 🔎 **filter_table_names()** - 智能搜索表名（模糊匹配）
- 📊 **schema_info()** - 深度解析表结构（列、主键、索引、外键）
- 🛡️ **execute_query()** - 安全执行SQL查询（仅SELECT，防注入）
- 🗄️ **get_database_info()** - 获取数据库连接信息
- 🔧 **多数据库支持** - PostgreSQL、MySQL、SQLite
- ⚙️ **连接池管理** - 自动连接池配置和监控
- 🐳 **Docker支持** - 一键启动多数据库环境

## 🏗️ 技术架构

- **框架**: FastMCP - 现代化的MCP服务器框架
- **数据库**: SQLAlchemy - 强大的数据库抽象层
- **支持数据库**: PostgreSQL、MySQL、SQLite
- **配置管理**: Pydantic Settings - 类型安全的配置管理
- **连接池**: SQLAlchemy QueuePool - 高效的连接池管理
- **包管理**: uv - 快速的Python包管理器
- **容器化**: Docker Compose - 一键部署多数据库环境
- **安全**: 完整的输入验证和SQL注入防护

## 🚀 快速开始

### 1. 安装依赖

```bash
# 使用uv包管理器（推荐）
uv sync

# 或使用pip
pip install -e .
```

### 2. 选择数据库类型

#### 选项A：使用SQLite（最简单）
```bash
# 创建SQLite测试数据库
python data/init_scripts/init_sqlite_db.py
```

#### 选项B：使用Docker启动多数据库环境
```bash
# 启动PostgreSQL和MySQL容器
docker-compose -f docker-compose.db.yml up -d

```


### 3. 启动MCP服务器

```bash
uv run python -m mcp_datatools.server
```

### 4. 在Cursor中配置

在Cursor的MCP配置中添加：

```json
{
  "mcpServers": {
    "mcp-datatools-sqlite": {
      "command": "uv",
      "args": ["run", "--project", "/path/to/project", "python", "-m", "mcp_datatools.server"],
      "env": {
        "DB_URL": "sqlite:///data/test.db"
      }
    },
    "mcp-datatools-postgres": {
      "command": "uv",
      "args": ["run", "--project", "/path/to/project", "python", "-m", "mcp_datatools.server"],
      "env": {
        "DB_URL": "postgresql://postgres:password@localhost:5432/testdb_1"
      }
    },
    "mcp-datatools-mysql": {
      "command": "uv",
      "args": ["run", "--project", "/path/to/project", "python", "-m", "mcp_datatools.server"],
      "env": {
        "DB_URL": "mysql+pymysql://testuser:testpass@localhost:3306/testdb_2"
      }
    }
  }
}
```

## 📚 使用示例

### 1. 获取所有表名
```
问AI：看看test.db有啥表？
```
<img width="912" height="393" alt="image" src="https://github.com/user-attachments/assets/54dcd1e4-7dad-4819-b40f-467092fc21f5" />



### 2. 智能搜索表名
```
问AI：找找用户相关的表
```
<img width="1031" height="493" alt="image" src="https://github.com/user-attachments/assets/d2717260-3740-4ce0-ac30-be286c4cd6a3" />


```
问AI：有哪些订单相关的表？
```
<img width="1038" height="489" alt="image" src="https://github.com/user-attachments/assets/f354e117-14c0-489d-976e-2b28e3ffbbd8" />


### 3. 分析表结构
```
问AI：users表的结构是什么样的？
```
<img width="1157" height="828" alt="image" src="https://github.com/user-attachments/assets/becb7b09-ae83-4d7a-a966-0ee31ef022c6" />

### 4. 执行SQL查询
```
问AI：查询users表中的所有数据
```
<img width="954" height="547" alt="image" src="https://github.com/user-attachments/assets/7c6201ed-9a89-4afb-8d20-666d124522d8" />

```
问AI：查询价格大于1000的产品
```
<img width="976" height="540" alt="image" src="https://github.com/user-attachments/assets/57771453-6aec-4003-a96c-54673680d032" />

```
问AI：查询每个用户的订单数量
```
<img width="707" height="706" alt="image" src="https://github.com/user-attachments/assets/5bc02e42-f847-407f-af94-5b011062ad4c" />


### 5. 获取数据库信息
```
问AI：查询mysql数据库testdb_2的信息
```
<img width="526" height="827" alt="image" src="https://github.com/user-attachments/assets/681ca681-48c5-4e7e-bc81-acf75f2ee888" />


```
问AI：testdb_1和testdb_2这2个数据库连接池状态如何？
```
<img width="538" height="790" alt="image" src="https://github.com/user-attachments/assets/d5a56830-933d-434a-abf9-e463206c2d6d" />

## 🛡️ 安全特性

- **只允许SELECT查询** - 防止数据泄露和意外修改
- **参数化查询** - 防止SQL注入攻击
- **自动LIMIT限制** - 防止大量数据返回
- **完整输入验证** - 确保查询安全性
- **错误处理** - 友好的错误提示和日志记录

## 📁 项目结构

```
mcp-datatools/
├── pyproject.toml              # 项目配置
├── docker-compose.db.yml       # Docker数据库环境
├── README.md                  # 项目说明
├── config/
│   ├── __init__.py
│   └── settings.py            # 配置管理
├── src/
│   └── mcp_datatools/         # 主包
│       ├── __init__.py
│       ├── server.py          # MCP服务器
│       ├── database.py        # 多数据库管理
│       └── utils.py           # 工具函数
├── data/
│   └── init_scripts/
│       ├── init_sqlite_db.py  # SQLite初始化脚本
│       ├── postgresql.sql     # PostgreSQL初始化脚本
│       └── mysql.sql          # MySQL初始化脚本
├── tests/
│   └── verify_functions.py    # 功能验证脚本
└── uv.lock                    # 依赖锁定文件
```

## 🔧 开发指南

### 运行测试
```bash
python tests/verify_functions.py
```

### 开发环境设置
```bash
# 克隆项目
git clone https://github.com/biao994/mcp-datatools.git
cd mcp-datatools

# 安装依赖
uv sync

# 创建测试数据库
python data/init_scripts/init_sqlite_db.py

# 启动开发服务器
uv run python -m mcp_datatools.server
```

## 📈 开发计划

- [x] **v1.0.0** - 基础框架和核心功能实现
  - 基础框架和SQLite支持
  - 表搜索、结构分析、安全查询功能
- [x] **v2.0.0** - 多数据库支持
  - PostgreSQL、MySQL、SQLite支持
  - 连接池管理和配置系统
  - Docker容器化支持
  - 完整的配置管理
- [ ] **v3.0.0** - 高级功能和性能优化
  - 查询性能优化
  - 高级数据分析功能
  - 监控和日志系统

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [FastMCP](https://github.com/pydantic/fastmcp) - 现代化的MCP服务器框架
- [SQLAlchemy](https://www.sqlalchemy.org/) - 强大的数据库抽象层
- [uv](https://github.com/astral-sh/uv) - 快速的Python包管理器

## 📞 联系方式

- 项目链接: [https://github.com/biao994/mcp-datatools](https://github.com/biao994/mcp-datatools)
- 作者: biao994
- 邮箱: zhengweibiao37@gmail.com

---

⭐ 如果这个项目对你有帮助，请给个 Star 支持一下！


