# src_v1/models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from src_v1.db import Base

# 用户表（登录注册用）
class UserDB(Base):
    __tablename__ = "user"#类的内置属性，固定写法。指定数据库里真实的表名为 `user`

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password = Column(String(100), nullable=False)
    #`Column`：用来声明表的字段；
    #`Integer`：该字段在 MySQL 中的数据类型为整数；
    #`primary_key=True`：标记该字段为主键，主键自动自带非空nullable、唯一unique、索引index；
    #`index=True`：给字段建立数据库索引，查询时可用字段查询（id/username）
    #String(50)：字符串类型，最大长度为50
    #unique=True：不允许重复
    #nullable=False ：不允许为空

    # 关系：一个用户有多条todo
    #`relationship` → ORM 对象关联;`back_populates` 用来配置双向关联，两边必须成对、名称对应
    #语义：一个 UserDB 实例对象，可以通过`.todos`，直接拿到属于这个用户的全部TodoDB对象集合
    todos = relationship("TodoDB", back_populates="owner")

# todo表，增加 user_id 外键，每条todo归属一个用户
class TodoDB(Base):
    __tablename__ = "todo"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String(200))
    is_done = Column(Boolean, default=False)
    create_time = Column(DateTime, default=datetime.now)
    #Python 自动调用`datetime.now`填充当前时间

    # 外键：关联用户.
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    owner = relationship("UserDB", back_populates="todos")
    #`ForeignKey("user.id")`：外键约束，写在多的一方。含义：当前 todo 表的 user_id，必须是 user 表 id 里面已经存在的值
    #一个 TodoDB 实例对象，可以通过 `.owner` 直接拿到对应的 UserDB 用户对象
    #`back_populates` 两边的名字必须互相对应

# ⚠️ 关键：执行这句，ORM自动扫描上面所有继承Base的类，没有表就自动创建
if __name__ == "__main__":
    from src_v1.db import engine
    Base.metadata.create_all(bind=engine)
    #指定使用这个 engine 去连接数据库、执行建表 SQL
