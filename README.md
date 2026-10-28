# TodoList 待办清单后端项目
基于 Python + FastAPI + SQLAlchemy + MySQL 待办清单接口项目
分v1,v2两个迭代版本

## ✨ 功能清单
### v1:基础功能
- 待办：创建、查询、修改、删除、分页筛选
- 数据校验：Pydantic参数校验
- MySQL持久化存储，ORM操作数据库
- FastAPI自动生成接口文档：`/docs`
- 环境变量配置：数据库连接地址放在`.env` 文件

### v2:新增功能
- 用户模块：注册、登陆
- 一对多外键关联：一个用户对应多条待办，用户之间数据隔离
- 级联删除：级联删除：删除用户时，该用户所有待办自动删除
- Alembic数据库迁移：安全修改表结构、版本回滚，无需删库重建
- 全局异常捕获：统一 `code/msg/data` 返回格式

## ✨ 项目目录总览
├── alembic               # 数据库迁移
 
├──alembic.ini            # Alembic 数据库迁移配置

├── src_v1/src_v2         # v1/v2版本

├── requirements.txt      # 项目依赖清单

├── .gitignore            # Git忽略配置

├── .env                  # 私有配置（数据库账号密码）

└── README.md             # 项目说明文档

### src_v2/

├── db.py                 # 数据库引擎、会话工厂、Base 基类、get_db 依赖

├── models.py             # ORM 数据表模型：UserDB、TodoDB，一对多外键关系,双向关联，级联删除

├── schemas.py            # Pydantic 模型：请求入参、统一响应 Resp、分页结构

├── crud.py               # 数据库 CRUD 封装：新增、修改、删除、分页查询、关键字模糊查询

└── main.py               # 项目入口：路由接口、全局异常捕获、接口启动

## 🚀 本地启动

1. 新建Python项目并在终端安装依赖
```
pip install -r requirements.txt
```
2. 新建名为.env文件，填入自己的MySQL连接信息
```
DATABASE_URL=mysql+pymysql://root:你的密码@127.0.0.1:3306/todo_db
```
3. 终端启动项目
```
uvicorn src_v2.main:app --reload
```
4. 启动成功后访问接口文档
```
http://127.0.0.1:8000/docs
```