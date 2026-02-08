# 说明

- 以 Python 3.10+ 为开发语言
- 采用 APIFlask 3.x 轻量级 Python Web API 框架
- 支持从 marshmallow / Pydantic schemas 自动生成 API 文档：
    * Swagger UI path： '/api/docs'
- 自动生成 OpenAPI spec 文件（路径：/openapi.json ）
- 引入 Marshmallow 库实现数据类型相互转换（序列化/反序列化/校验）
- 采用 AWS SDK for Python (Boto3) 创建、管理各项AWS服务/资源
- 采用 Cloud Control API 对受支持资源通过统一的方法实现生命周期管理
- 基于蓝图(Blueprint)对功能模块进行拆分，一个目录/文件就是一个功能模块

## 技术栈

| 组件 | 版本 |
|---|---|
| Flask | 3.1 |
| APIFlask | 3.0 |
| Flask-SQLAlchemy | 3.1 |
| Flask-Migrate | 4.1 |
| Marshmallow | 4.x |
| Boto3 | 1.36+ |

## 启动项目

clone:
```
$ git clone https://github.com/aleck31/Easyun.git
$ cd Easyun/server
```

create & activate virtual env then install dependency:
```
$ python3 -m venv .venv
$ source .venv/bin/activate  # use `.venv\Scripts\activate` on Windows
$ pip install -r requirements/min.txt
```

configure environment variables:
```
$ cp .env.example .env
# edit .env to set your own SECRET_KEY, database URI, etc.
```

initialize database:
```
$ flask initdb
```

run:
```
$ python3 run.py
```

api docs:
open url: http://127.0.0.1:6660/api/docs with browser

### 相关命令

1. 初始化数据库
```
$ flask initdb
```
2. 删除数据库
```
$ flask dropdb
```
3. 迁移数据库
```
$ flask db init       # 初始化migrate仓库
$ flask db migrate -m "<your commit message>"  # 创建迁移脚本文件
$ flask db upgrade    # 运行更新脚本迁移数据库
```

# 目录结构

```
└─server
    ├─.venv                     本地虚拟环境
    ├─easyun                
    │  ├─common                 通用组件
    │  │  ├─auth.py             认证模块
    │  │  ├─models.py           模型定义
    │  │  ├─schemas.py          Schema定义
    │  │  ├─result.py           返回响应体定义
    │  │  └─init_db.py          数据库初始化
    │  ├─libs                   工具库
    │  │  ├─task_manager.py     异步任务管理
    │  │  ├─log/                日志模块
    │  │  └─utils.py            公共工具
    │  ├─cloud                  云平台功能组件
    │  ├─config                 AWS配置文件(JSON)
    │  ├─base.db                数据库文件       
    │  └─modules                功能模块
    │     ├─account             账户管理BP
    │     ├─dashboard           监控面板BP
    │     ├─datacenter          数据中心管理BP
    │     ├─mbackup             备份管理BP
    │     ├─mserver             服务器管理BP
    │     ├─mstorage            存储管理BP
    │     ├─mdatabase           数据库管理BP
    │     └─mloadbalancer       负载均衡BP
    ├─deployment                应用部署   
    ├─logs                      运行日志
    ├─requirements              环境依赖
    ├─migrations                数据库migration文件 
    ├─config.py                 配置文件
    └─run.py                    启动脚本
```
