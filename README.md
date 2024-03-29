# 说明

- 以python为开发语言，结合 notebook 方便验证、调试SDK各项功能
- 采用 APIFlask 轻量级 Python Web API 框架，用于api
- 支持从marshmallow schemas自动生成 API 文档：
    * Swagger UI path： '/api/docs'
    * Redoc path：      '/api/redoc' 
- 自动生成 OpenAPI spec 文件（路径：/openapi.json ）
- 引入Marshmallow库实现数据类型相互转换：
    * json string -> dict，json string -> list，json string -> object
    * object -> dict， objects -> json string, object -> list
    * dict -> object，list -> object
- 采用 AWS SDK for Python (Boto3) 创建、管理各项AWS服务/资源；
- 采用 Cloud Control API 对受支持资源通过统一的方法实现生命周期管理；
- 基于蓝图(BlurPrint)对功能模块进行拆分，一个目录/文件就是一个功能模块

## 启动项目

clone:
```
$ git clone https://github.com/aleck31/Easyun.git
$ cd Easyun/server
```

create & activate virtual env then install dependency:
with venv + pip:
```
$ python -m venv env  # use `virtualenv env` for Python2, use `python3 ...` for Python3 on Linux & macOS
$ source env/bin/activate  # use `env\Scripts\activate` on Windows
$ pip install -r requirements/min.txt
```

run:
with flask cli:
```
$ flask run -p 6660
* Running on http://127.0.0.1:6660/
```
with python:
```
$ python run.py # use python3 run.py for python3 on Linux & macOS
```

api docs:
open url: http://127.0.0.1:6660/ with browser

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
$ flask db init # 初始化migrate仓库
$ flask db migrate -m "<your commit message>" # 创建迁移脚本文件
$ flask db upgrade # 运行更新脚本迁移数据库
```

# 目录结构

```
└─server
    ├─.venv                     本地虚拟环境
    ├─easyun                
    │  ├─common                 通用组件
    │  │  ├─auth.py             认证模块
    │  │  ├─models.py           模型定义
    │  │  ├─schema.py           Schema定义
    │  │  ├─utils.py            公共组件
    │  │  └─result.py           返回响应体定义
    │  ├─libs                   通用组件
    │  ├─cloud                  云平台功能组件
    │  ├─base.db                数据库文件       
    │  └─modules                功能组件
    │     ├─account             账户管理BP
    │     ├─dashboard           监控面板BP
    │     ├─datacenter          数据中心管理BP
    │     ├─mbackup             备份管理BP
    │     ├─mnetwork            网络管理BP
    │     ├─mserver             服务器管理BP
    │     ├─mstorage            存储管理BP
    │     └─mdatabase           数据库管理BP      
    ├─deployment                应用部署   
    ├─logs                      运行日志
    ├─requirements              环境依赖
    ├─migrations                数据库migration文件 
    ├─demo.py                   APIFlask演示项目
    ├─config.py                 配置文件
    └─run.py                    启动脚本
```
