from os import getenv

from  sqlalchemy import  create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from  dotenv import  load_dotenv
import  os

#加载.env
#读取项目里的`.env`，把里面配置加载到系统环境变量，用来存放敏感信息
load_dotenv()

#读数据库连接串
DATABASE_URL=os.getenv("DATABASE_URL")

#创建数据库引擎，
engine=create_engine(DATABASE_URL)

#Session是SQLAlchemy 自带的基础父类。调用sessionmaker后，生成定制化配置好的子类SessionLocal，生成单次请求独立的数据库会话实例db
SessionLocal=sessionmaker(autocommit=False,autoflush=True,bind=engine)

#创建ORM模型的基类
Base=declarative_base()

#依赖函数 获得会话对象
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
