# crud.py 伪代码
# 导入 Session、models里的UserDB、TodoDB
from sqlalchemy import select, insert, update, delete, func  # SQL描述语句
from sqlalchemy.orm import Session #内含方法.add/.commit/.refresh/.scalar(查第一个/None)，执行SQL语句，写进数据库
from src_v2.models import UserDB,TodoDB


# 用户相关
def get_user_by_username(db:Session, username:str): #db是子类SessionLocal的实例，也是父类Session的实例，向上兼容
    stmt=select(UserDB).where(UserDB.username==username)# SQL描述语句：查询UserDB，匹配username
    user=db.scalar(stmt)# 返回第一条,为ORM实例
    return user

def get_user_id(db:Session, user_id:int):
    stmt = select(UserDB).where(UserDB.id==user_id)  # SQL描述语句：查询UserDB，匹配username
    user_id = db.scalar(stmt)  # 返回第一条,为ORM实例
    return user_id

def create_user(db:Session, username:str, password:str):
    db_user=UserDB(username=username,password=password)# 在内存构造UserDB实例
    db.add(db_user)# add，加入session会话缓存
    db.commit()# commit，提交事务
    db.refresh(db_user)# refresh
    return db_user# 返回用户orm对象

# todo相关;
def create_todo(db:Session, user_id:int, content:str):
    db_todo=TodoDB(user_id=user_id,content=content)# 构造TodoDB实例，绑定user_id
    db.add(db_todo)# add
    db.commit()# commit
    db.refresh(db_todo)# refresh
    return db_todo# 返回todo orm对象

def get_todo_by_id(db:Session, todo_id:int, user_id:int): #按todo_id和user_id查todo
    # 查询TodoDB，同时匹配todo_id 和 user_id，返回第一条
    stmt=select(TodoDB).where(TodoDB.id==todo_id,TodoDB.user_id==user_id)
    todo=db.scalar(stmt)
    return todo

def get_todo_by_content(db:Session, content:str, user_id:int):#按content和user_id查todo
    # 查询TodoDB，同时匹配todo_id 和 user_id，返回第一条
    stmt=select(TodoDB).where(TodoDB.content==content,TodoDB.user_id==user_id)
    todo=db.scalar(stmt)
    return todo

def get_todo_page_list(db:Session, user_id:int, page:int, page_size:int, keyword:str=""):
    # 基础查询：筛选user_id
    stmt=select(TodoDB).where(TodoDB.user_id==user_id)
    if keyword:  # 如果keyword不为空，追加like模糊查询
        stmt=stmt.where(TodoDB.content.like(f'%{keyword}%'))

    count_stmt=select(func.count()).select_from(stmt.subquery()) #统计虚拟表里共有几行记录
    #.subquery() 创建临时虚拟表； select_from(表) 接下来从哪张表取数据
    #func.count(字段) 计数

    total=db.scalar(count_stmt) # 拿到单个值，统计总数total
    # 计算offset
    offset=(page-1)*page_size #从第几条开始

    # 给查询加上分页：offset跳过前面数据，limit取当前页数量
    page_stmt=stmt.offset(offset).limit(page_size)
    # 遍历items，转为字典列表
    items=db.scalars(page_stmt).all() #scalars返回多行

    item_list=[  #orm对象转字典
        {
            'id':user_id,
            'content':item.content,
            'is_done':item.is_done,
            'create_time':item.create_time
            }
        for item in items
    ]

    return {
        "total":total,
        "page":page,
        "page_size":page_size,
        "items":item_list
    }


def update_todo_item(db:Session, todo_id:int, user_id:int, content:str, is_done:bool):
    # 调用get_todo_by_id查询todo
    stmt=select(TodoDB).where(TodoDB.user_id==user_id,TodoDB.id==todo_id)
    todo=db.scalar(stmt)  #查到并返回 TodoDB 对象

    if todo is None:
        return None         #todo不存在返回None
    # 入参不为None则赋值更新字段
    if content is not None:
        todo.content=content
    if is_done is not None:    # commit、refresh
        todo.is_done=is_done

    db.commit()
    db.refresh(todo)
    return todo
        # 返回更新后的todo

def delete_todo_item(db:Session, todo_id:int, user_id:int):
    stmt=select(TodoDB).where(TodoDB.id==todo_id,TodoDB.user_id==user_id)
    todo=db.scalar(stmt)
    if todo is None:
        return None
    else:
        db.delete(todo)
        db.commit()
        return True
    # todo不存在返回False
    # db.delete
    # commit
    # 返回True

def delete_user(db:Session, user_id:int): #user_id写在入参，默认为query参数
    stmt=select(UserDB).where(UserDB.id==user_id)
    user=db.scalar(stmt)
    if user is None:
        return None
    else:
        db.delete(user)
        db.commit()
        return True