from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from src_v2.crud import create_user, get_user_by_username, create_todo, get_todo_page_list, get_todo_by_id, \
    update_todo_item, delete_todo_item, get_todo_by_content, get_user_id, delete_user
from src_v2.db import Base, get_db, engine
from src_v2.schemas import Resp, UserRegister, UserLogin, TodoCreate, PageTodo, TodoUpdate

#初始化FastAPI应用
app=FastAPI()
Base.metadata.create_all(bind=engine)

#注册全局异常处理器，统一包装返回格式Resp
@app.exception_handler(HTTPException)  #HTTPException 是走异常通道，默认返回格式 `{"detail":"xxx"}`
async def http_err_handler(request,exc:HTTPException):
    return JSONResponse(content=Resp(code=exc.status_code,msg=exc.detail,data=None).model_dump(),
                        status_code=exc.status_code)
#content=是在响应体，status_code=是在响应头

# 用户注册接口
@app.post('/register')
def register(user:UserRegister,db:Session=Depends(get_db)): #接收用户名、密码
    # Python 规定，有默认值的参数，不能写在无默认值参数前面,user在前，db在后
    exist=get_user_by_username(db, user.username)
    if exist:
        raise HTTPException(status_code=400,detail='用户已存在') #查询用户名是否已存在，存在则抛400
    new_user=create_user(db, user.username, user.password) #调用crud.create_user新建用户
    return Resp(code=200,msg='注册成功',data=f'id={new_user.id}') #返回成功Resp，带上user_id

#用户登陆接口
@app.post('/login')
def login(user:UserLogin,db:Session=Depends(get_db)):  #接收用户名、密码
    db_user=get_user_by_username(db, user.username)
    if db_user is None or db_user.password !=user.password:#查询用户，校验密码是否匹配
        raise HTTPException(status_code=400,detail='用户名或密码错误')#校验失败抛400
    return  Resp(code=200,msg='登陆成功',data=f'id={db_user.id}')#返回成功Resp，带上user_id

# Todo接口
@app.post('/todo')
def create_todo_item( todo:TodoCreate, user_id:int=Query(...) , db:Session=Depends(get_db) ): #接收todo内容、user_id
    db_user=get_user_id(db, user_id)#先查用户是否存在
    if db_user is None:
        raise HTTPException(status_code=400, detail='用户不存在')
    exist_todo=get_todo_by_content(db, todo.content,user_id) #再查该用户有无重复待办
    if exist_todo is not None:
        raise HTTPException(status_code=400,detail='待办已存在')
    new_todo=create_todo(db, db_user.id, todo.content) #调用crud.create_todo创建新待办
    return Resp(code=200,msg='新增待办成功',data=f'待办内容:{new_todo.content}') #返回成功Resp，带上todo_id

@app.get('/todo')
def get_todo_by_keyword(
    user_id:int=Query(default=...),
    page:int=Query(default=...,ge=1),
    page_size:int=Query(default=10,ge=1,le=100),
    keyword:str=Query(default=...),  #default=... 表示必传，否则报错
    db:Session=Depends(get_db)
):  #接收user_id、page、page_size、keyword
    uer_id = get_user_id(db, user_id)  # 先查用户是否存在
    if uer_id is None:
        raise HTTPException(status_code=400, detail='用户不存在')#先查用户在不在
    todo_list=get_todo_page_list(db, user_id, page, page_size, keyword) #调用crud.get_todo_page_list获取分页数据
    #变量类型注解只写在形参里，调用函数时不写
    return Resp(code=200,msg='分页查询成功',data=todo_list)   #返回分页Resp

@app.get('/todo/{todo_id}') #根据待办查用户
def get_todo_by_todo_id(
    todo_id:int,
    user_id:int=Query(default=...),
    db:Session=Depends(get_db)
): #接收todo_id、user_id
    todo=get_todo_by_id(db, todo_id,user_id)#todo_crud查询todo，不存在抛404
    if todo is None:
        raise HTTPException(status_code=404,detail='待办不存在或不属于当前用户')
    return Resp(code=200,msg='查询成功',data=f'待办内容:{todo.content}')

@app.put('/todo/{todo_id}')
def update_todo(
    todo_id:int,
    todo_data:TodoUpdate,
    user_id:int =Query(...),
    db:Session = Depends(get_db)
):#接收todo_id、待办更新字段、user_id
    todo=update_todo_item(db, todo_id, user_id, todo_data.content,todo_data.is_done)
    if todo is None:# todo不存在
        raise HTTPException(status_code=404,detail='更新失败') #更新失败抛404
    return Resp(code=200,msg='更新成功',data=todo.content)

@app.delete('/todo/{todo_id}') #删除待办
def delete_todo(
    todo_id:int,
    user_id:int =Query(...),
    db:Session =Depends(get_db)
): #接收todo_id、user_id
    todo=delete_todo_item(db, todo_id, user_id)#调用crud.delete_todo_item
    if todo is None:
        raise HTTPException(status_code=404,detail='删除失败')
    return Resp(code=200,msg='删除成功',data=None)

@app.delete('/user') #删除用户
def delete_todo(
    user_id:int=Query(...),
    db:Session =Depends(get_db)
):
    user=delete_user(db, user_id) #调用crud.delete_todo_item
    if user is None:
        raise HTTPException(status_code=404,detail='删除失败')
    return Resp(code=200,msg='删除成功',data=None)

# 启动入口
if __name__=='__main__':
    import uvicorn
    uvicorn.run("src_v2.main_copy:app", port=8000, reload=True)
    #0.0.0.0绑定本机所有网卡：同WiFi/有线/虚拟,访问：`http://内网IP:8000/docs` 就能打开接口文档
