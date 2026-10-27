from datetime import datetime
from sqlalchemy.orm import relationship
from src_v2.db import Base, engine
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey

#UserDB类，继承Base
class UserDB(Base):
    __tablename__="user" #表名user；写错下划线，SQLAlchemy 识别不到这个配置，会自动用类名当表名
    id=Column(Integer,primary_key=True) #id 主键
    username=Column(String(50),unique=True,nullable=False) #username 唯一字符串
    password=Column(String(100),unique=False,nullable=False) #过长会数据库报错
    create_time=Column(DateTime,default=datetime.now) #datetime.now为函数，每次使用时调用生成

    todos=relationship("TodoDB",back_populates='owner',cascade="all, delete-orphan",
    passive_deletes=True)

    #relationship=(argument关联的模型类名字，back_populates=''双向关联)  users.todos

#TodoDB类，继承Base
class TodoDB(Base):
    __tablename__="todos" #表名todos
    id=Column(Integer,primary_key=True)  #id 主键
    content=Column(String(100),nullable=False)
    is_done=Column(Boolean,nullable=False, default=False) #nullable默认为null，出现null/True/False
    create_time=Column(DateTime,default=datetime.now)
    #owner_id 外键指向user.id; ondelete='CASCADE级联' :主表删除时子表跟着一起删除
    user_id=Column(Integer,ForeignKey('user.id',ondelete='CASCADE'),nullable=False)
    #关联：todos.owner
    owner=relationship("UserDB",back_populates='todos')

if __name__=='__main__':
    from src_v2 import engine
    Base.metadata.create_all(bind=engine)

