#接收参数、参数校验、调用 crud 函数、包装返回结果
# src_v1/main.py
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from src_v1.db import engine, Base, get_db
from src_v1.models import UserDB, TodoDB
from src_v1.schemas import UserRegister, UserLogin, TodoCreate, TodoUpdate, Resp
from src_v1.crud import (
    get_user_by_username, create_user,
    create_todo, get_todo_by_id, get_todo_page_list,
    update_todo_item, delete_todo_item
)
from fastapi.responses import JSONResponse

# 启动时自动建表（表不存在则创建，表存在则不变）
#Base 自带的关键属性：`metadata`，自动收集所有继承 Base 的表结构信息
#`create_all()` 只会创建不存在的表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Todo-ORM项目，带登录注册分页筛选")

# ---------------- 全局异常捕获，统一返回格式 ----------------
#`@app.exception_handler(异常类型)`：FastAPI 的异常处理器装饰器
#`HTTPException`：FastAPI 内置的异常类
#`async`：异步标记；request：当次的HTTP请求对象；exc是HTTPException类的实例
@app.exception_handler(HTTPException)
async def http_err_handler(request, exc: HTTPException):
    return JSONResponse( #FastAPI 的响应类，直接构造一个 JSON 格式的 HTTP 响应返回给前端
        content=Resp(code=exc.status_code, msg=exc.detail, data=None).model_dump(),
        status_code=exc.status_code  #`status_code=`：HTTP 协议层面的响应状态码
    )
#`JSONResponse`：FastAPI 的响应类，直接构造一个 JSON 格式的 HTTP 响应返回给前端；JSONResponse(content=字典, status_code=数字)
#`.model_dump()`：Pydantic的方法，把 Resp 模型实例转换成 Python 字典，JSONResponse 才能序列化输出

# ---------------- 用户接口：注册、登录 ----------------
#`@app.post()`：FastAPI 路由装饰器
@app.post("/register", response_model=Resp)
#response_model=Resp  指定这个接口返回的数据必须按照 Resp 这个 Pydantic 模型校验、格式化
def register(user: UserRegister, db: Session = Depends(get_db)):
    #`Depends(get_db)` FastAPI 的依赖注入标记，告诉接口：执行接口之前，先跑一遍 get_db，拿到 yield 出来的值，传给参数
    exist = get_user_by_username(db, user.username)  #调用 crud 函数 `get_user_by_username`，去数据库查这个用户名是否存在
    if exist:
        raise HTTPException(status_code=400, detail="用户名已存在")
    new_user = create_user(db, user.username, user.password)
    return Resp(code=200, msg="注册成功", data={"user_id": new_user.id})


@app.post("/login", response_model=Resp)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = get_user_by_username(db, user.username)
    if db_user is None or db_user.password != user.password:
        raise HTTPException(status_code=400, detail="账号或密码错误")
    return Resp(code=200, msg="登录成功", data={"user_id": db_user.id})


# ---------------- Todo接口：CRUD + 分页筛选 ----------------
@app.post("/todo", response_model=Resp)
def add_todo(
    todo: TodoCreate,
    user_id: int = Query(..., description="登录返回的user_id"),  #`description`：接口文档（/docs）里的说明文字
    #`Query()`：告诉 FastAPI：这个参数从url 查询参数（query 参数）拿
    #default:... 表示参数必填，不填报错
    db: Session = Depends(get_db)
):
    new_todo = create_todo(db, user_id, todo.content)
    return Resp(code=200, msg="新增待办成功", data={"todo_id": new_todo.id})


@app.get("/todo", response_model=Resp)
def query_todo_list(
    user_id: int = Query(...),
    page: int = Query(1, ge=1), #`ge=1`：限制参数必须 ≥1
    page_size: int = Query(10, ge=1, le=100), #`le=100`：一页最多 100 条
    keyword: str = Query("", description="搜索待办内容"),
    #`default=""`：不传关键词默认是空字符串 → 不做模糊搜索，返回该用户全部待办
    db: Session = Depends(get_db)
):
    page_data = get_todo_page_list(db, user_id, page, page_size, keyword)
    return Resp(code=200, msg="查询成功", data=page_data)


@app.get("/todo/{todo_id}", response_model=Resp)
#路径参数：唯一标识一个资源(单条),写在url大括号{变量1}里，函数里直接写变量1
def get_single_todo(
    todo_id: int,
    user_id: int = Query(...), #查询参数，在url？后面，在变量后加Query(...)
    db: Session = Depends(get_db)
):
    todo = get_todo_by_id(db, todo_id, user_id)
    if not todo:
        raise HTTPException(status_code=404, detail="待办不存在或不属于当前用户")
    return Resp(code=200, msg="查询成功", data={
        "id": todo.id,
        "content": todo.content,
        "is_done": todo.is_done,
        "create_time": todo.create_time
    })

@app.put("/todo/{todo_id}", response_model=Resp)
def update_todo(
    todo_id: int,
    todo: TodoUpdate,
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    updated = update_todo_item(db, todo_id, user_id, todo.content, todo.is_done)
    if updated is None:
        raise HTTPException(status_code=404, detail="待办不存在或不属于当前用户")
    return Resp(code=200, msg="修改成功")

@app.delete("/todo/{todo_id}", response_model=Resp)
def delete_todo(
    todo_id: int,
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    ok = delete_todo_item(db, todo_id, user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="待办不存在或不属于当前用户")
    return Resp(code=200, msg="删除成功")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src_v1.main:app", host="0.0.0.0", port=8000, reload=True)
    #"src_v1.main:app"  模块名: 变量名
    #`0.0.0.0`：允许同局域网其他机器访问
    #port=8000 :服务跑在 8000 端口
    #reload ：热重载，修改代码保存后，服务自动重启