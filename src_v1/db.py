# src_v1/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# 默认加载名为.env的文件，写入进程环境变量
load_dotenv()#读取.env文件内容，解析里面KEY=VALUE格式的行

# 读取数据库连接串；`os.getenv(key)`：获取进程环境变量中`key`对应的value值
DATABASE_URL = os.getenv("DATABASE_URL")

# 创建数据库引擎（ORM核心） DATABASE_URL：数据库地址字符串
engine = create_engine(DATABASE_URL) #作用：保存数据库地址/账号密码等配置，管理数据库连接

# 会话工厂，每次请求拿一个数据库会话，返回一个类，类名为SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#autocommit：自动事务提交，关闭后需手动db.commit()提交到数据库
#`autoflush=True`是默认值：每次执行查询`db.query()`之前，会自动执行 flush，把内存变更刷到数据库

# 返回一个类，类名为Base；ORM模型的父类，每张数据表的类都继承Base后，SQLAlchemy能识别，这个类映射数据库里的一张表
Base = declarative_base()


# 依赖函数：获取数据库会话（对应你原来的 get_db()）
def get_db():
    db = SessionLocal() #实例化SessionLocal这个类，得到 ORM会话对象  db 的类型就是：Session
    #`db` 是 ORM 会话对象，ORM 的`.add()` `.query()` `.commit()` `.rollback()` 等方法都挂载在这个对象上
    try:
        yield db
    #`Depends(get_db)`拿到这个产出的`db`，传给接口函数使用,接口业务代码执行期间，这个函数停在 `yield` 这一行
    finally:
        db.close()
