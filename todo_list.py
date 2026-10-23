from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
from sqlalchemy import Column,Integer,String,Boolean
from fastapi import FastAPI,Depends,HTTPException

from dotenv import load_dotenv
import os

# 加载 .env 文件
load_dotenv()

# 读取环境变量
database_url= os.getenv("DATABASE_URL")

#连接数据库
engine=create_engine(database_url)
Sessionlocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)
base=declarative_base()

#用类定义表结构
class TodoDB(base):
    __tablename__='todo'
    id=Column(Integer,primary_key=True,index=True)
    content=Column(String(200))
    is_done=Column(Boolean,default=False)
#自动建表
base.metadata.create_all(bind=engine)

app=FastAPI()
#依赖函数
def get_db():
    db=Sessionlocal()
    try:
        yield db
    finally:
        db.close()

#get接口
@app.get('/todos')
def get_all_todos(db=Depends(get_db)):
    todo_list=db.query(TodoDB).all()
    return todo_list

#post接口
class TodoCreate(BaseModel):
    content:str#参数校验

@app.post('/todos')#post不能直接浏览器地址栏访问
def create_todo(todo:TodoCreate,db=Depends(get_db)):
    new_todo=TodoDB(content=todo.content)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo

# PUT修改接口
class TodoUpdate(BaseModel):
    content: str
    is_done: bool

@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, todo: TodoUpdate, db=Depends(get_db)):  # 根据id查找待办： .filter() 加查询条件，.first() 只取匹配到的第一条
    todo_item = db.query(TodoDB).filter(TodoDB.id == todo_id).first()
    # 如果没找到，抛出404
    if not todo_item:
        raise HTTPException(status_code=404, detail="这条待办不存在")
    # 赋值新内容、新状态
    todo_item.content = todo.content
    todo_item.is_done = todo.is_done
    db.commit()  # 提交数据库
    db.refresh(todo_item)  # 同步更新
    return todo_item  # 返回更新后的结果

#DELETE删除接口
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db = Depends(get_db)):
    todo_item = db.query(TodoDB).filter(TodoDB.id == todo_id).first()
    if not todo_item:
        raise HTTPException(status_code=404, detail="这条待办不存在")
    db.delete(todo_item)
    db.commit()
    return {"msg": "删除成功"}