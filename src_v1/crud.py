#专门放对数据库的增、查、改、删（CRUD）逻辑，把数据库操作单独抽出来，不和接口代码混在一起
# src_v1/crud.py
from src_v1.models import UserDB, TodoDB
from sqlalchemy import select, insert, update, delete, func  # SQL描述语句
from sqlalchemy.orm import Session #`Session`：数据库会话,内含方法.add/.commit/.refresh/.scalar(查第一个/None)，执行SQL语句，写进数据库


# ========== 用户 CRUD ==========
def get_user_by_username(db:Session, username): #db是子类SessionLocal的实例，也是父类Session的实例，向上兼容
    stmt=select(UserDB).where(UserDB.username==username)# SQL描述语句：查询UserDB，匹配username
    user=db.scalar(stmt)# 返回第一条,为ORM实例
    return user

def create_user(db: Session, username: str, password: str):
    """新建用户"""
    db_user = UserDB(username=username, password=password)
    #在内存里造对象，没有进数据库
    db.add(db_user)
    db.commit()
    db.refresh(db_user)#去数据库重新读取这条刚插入的数据，把数据库自动生成的值，回填给 db_user 对象
    return db_user
    #新增三件套固定模板：`造对象 → add → commit → refresh`


# ========== Todo CRUD ==========
def create_todo(db: Session, user_id: int, content: str):
    """创建todo，绑定所属用户id"""
    db_todo = TodoDB(user_id=user_id, content=content) #TodoDB是ORM类，db_todo是ORM对象，在内存里
    db.add(db_todo) #ORM 对象加入当前 session 会话，只是标记，不发 SQL 到数据库；
    db.commit()  #数据写入MySQL
    db.refresh(db_todo) #再次查数据库，把数据库自动生成的字段同步会Python对象
    return db_todo


def get_todo_by_id(db: Session, todo_id: int, user_id: int):
    """根据id获取todo，必须校验user_id，用户只能访问自己的todo"""
    stmt = select(TodoDB).where(TodoDB.id == todo_id, TodoDB.user_id == user_id)
    todo = db.scalar(stmt)
    return todo


def get_todo_page_list(db: Session, user_id: int, page: int, page_size: int, keyword: str = ""):  #keyword为字符串，默认为空字符串
    #分页 + 关键词筛选
    stmt=select(TodoDB).where(TodoDB.user_id==user_id)
    if keyword:  # 如果keyword不为空，追加like模糊查询
        stmt=stmt.where(TodoDB.content.like(f'%{keyword}%'))
            #`like`：mysql 模糊匹配
            #`%` = 通配符，匹配任意文字
            #`%牛奶%` 代表内容里只要包含 “牛奶” 两个字就能搜到

    count_stmt=select(func.count()).select_from(stmt.subquery()) #统计虚拟表里共有几行记录
        #.subquery() 创建临时虚拟表； select_from(表) 接下来从哪张表取数据
        #func.count(字段) 计数

    total=db.scalar(count_stmt) # 拿到单个值，统计总数total
        # 计算offset
    offset=(page-1)*page_size #从第几条开始

        # 给查询加上分页：offset跳过前面数据，limit取当前页数量
    page_stmt=stmt.offset(offset).limit(page_size)
        # 遍历items，转为字典列表
    items=db.scalar(page_stmt).all()

    item_list=[  # 列表推导式，把 ORM 对象转字典  item_list = [ {"id": item.id ... } for item in items ]
        {
            'id':item.id,
            'content':keyword,
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

def update_todo_item(db: Session, todo_id: int, user_id: int, content=None, is_done=None):
    todo = get_todo_by_id(db, todo_id, user_id)
    if todo is None:
        return None
    if content is not None:
        todo.content = content
    if is_done is not None:
        todo.is_done = is_done
    db.commit()
    db.refresh(todo)
    return todo


def delete_todo_item(db: Session, todo_id: int, user_id: int):
    todo = get_todo_by_id(db, todo_id, user_id)
    if todo is None:
        return None
    db.delete(todo)
    db.commit()
    return True

