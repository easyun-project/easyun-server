# Easyun Server

AWS 云资源管理平台 API 服务端

- 基于 Python 3.12+，采用 APIFlask 轻量级 Web API 框架
- 自动生成 OpenAPI spec 和 API 文档（Swagger UI：`/api/docs`）
- 基于 marshmallow 实现数据序列化/反序列化/校验
- 采用 AWS SDK for Python (Boto3) 管理 AWS 服务/资源
- 基于蓝图(Blueprint)按功能模块拆分，支持多云扩展架构

## 技术栈

| 组件 | 版本 |
|---|---|
| Python | ≥3.12 |
| Flask | 3.1 |
| APIFlask | 3.1 |
| Flask-SQLAlchemy | 3.1 |
| Flask-Migrate | 4.1 |
| marshmallow | 4.x |
| boto3 | 1.36+ |
| uv | 包管理 |

## 快速开始

clone:
```
$ git clone https://github.com/aleck31/Easyun.git
$ cd Easyun/server
```

install dependencies:
```
$ uv sync
```

configure environment variables:
```
$ cp .env.example .env
# edit .env to set your own SECRET_KEY, database URI, etc.
```

initialize database:
```
$ uv run flask initdb
```

run:
```
$ uv run python run.py
```

API docs: http://127.0.0.1:6660/api/docs

### 常用命令

```bash
uv sync                              # 安装依赖
uv run python run.py                  # 启动服务
uv run flask initdb                   # 初始化数据库
uv run flask dropdb                   # 删除数据库
uv run python scripts/export_spec.py  # 导出 OpenAPI spec
```

数据库迁移：
```bash
uv run flask db init                  # 初始化 migrate 仓库
uv run flask db migrate -m "message"  # 创建迁移脚本
uv run flask db upgrade               # 执行迁移
```

## 项目结构

```
easyun-server/
├── easyun/                         # 主包
│   ├── __init__.py                 # App factory (create_app)
│   ├── common/                     # 通用组件
│   │   ├── auth.py                 # 认证模块 (HTTPTokenAuth)
│   │   ├── models.py              # 数据模型 (User/Account/Datacenter)
│   │   ├── schemas.py             # 通用 Schema
│   │   ├── result.py              # 统一响应封装
│   │   ├── account.py             # 云账号业务逻辑
│   │   └── dc_utils.py            # Datacenter 工具函数
│   ├── providers/                  # 云平台 SDK（多云架构）
│   │   ├── __init__.py            # 多云入口 (get_cloud, get_deploy_env)
│   │   ├── base.py                # 抽象基类
│   │   └── aws/                   # AWS 实现
│   │       ├── session.py         # boto3 session 管理
│   │       ├── region.py          # Region 信息
│   │       ├── utils.py           # AWS 工具函数
│   │       ├── datacenter.py      # DataCenter 聚合类
│   │       ├── resource/          # 云资源 SDK（按类型分类）
│   │       │   ├── compute/       # EC2, AMI, Instance Type
│   │       │   ├── storage/       # S3 Bucket, EBS Volume
│   │       │   ├── network/       # Subnet, SG, RouteTable, Gateway, EIP, ELB
│   │       │   └── database/      # RDS
│   │       └── management/        # 管理服务
│   │           ├── sdk_pricing.py # 定价查询
│   │           ├── sdk_quotas.py  # 配额查询
│   │           ├── sdk_cost.py    # 成本查询
│   │           └── sdk_tagging.py # 资源标签
│   ├── modules/                    # API 蓝图模块
│   │   ├── dashboard/             # 监控面板
│   │   ├── datacenter/            # 数据中心管理
│   │   ├── mserver/               # 服务器管理
│   │   ├── mstorage/              # 存储管理
│   │   ├── mdatabase/             # 数据库管理
│   │   ├── mloadbalancer/         # 负载均衡管理
│   │   ├── mbackup/               # 备份管理
│   │   └── account/               # 账号管理
│   ├── libs/                       # 工具库
│   │   ├── task_manager.py        # 异步任务管理
│   │   └── log/                   # 日志模块
│   └── config/                     # AWS 静态配置 (JSON)
├── scripts/
│   └── export_spec.py             # OpenAPI spec 导出
├── config.py                       # Flask 配置
├── run.py                          # 启动脚本
├── pyproject.toml                  # 项目配置 (uv)
└── .env.example                    # 环境变量模板
```

## 参与贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feat/my-feature`)
3. 提交更改 (`git commit -m 'feat: add some feature'`)
4. 推送到分支 (`git push origin feat/my-feature`)
5. 提交 Pull Request

请遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：`feat:`、`fix:`、`refactor:`、`docs:`、`build:`

## 许可证

本项目采用 [Apache License 2.0](LICENSE) 许可。
