# src_v1/schemas.py 规定前端发给后端的数据长什么样、后端返回给前端的数据长什么样，同时自动做类型校验
from pydantic import BaseModel
from typing import Optional, List, Any#类型标注工具
#Pydantic 模型，用来校验前端传入的数据、控制返回给前端的数据格式
#`BaseModel` 是 Pydantic 的基类。继承之后自动获得数据校验、类型解析能力。
#- `Optional`：这个字段可以不传，或者传 null； `List`：代表列表； `Any`：任意类型

# ---------------- 用户相关 请求模型 ----------------
class UserRegister(BaseModel): #注册接口接收的参数
    username: str
    password: str


class UserLogin(BaseModel): #登陆接口接收的参数
    username: str
    password: str


# ---------------- Todo相关 请求模型 ----------------
class TodoCreate(BaseModel):  #新增待办
    content: str


class TodoUpdate(BaseModel):  #修改待办
    content: Optional[str] = None
    is_done: Optional[bool] = None


# ---------------- 统一接口返回格式 ----------------
class Resp(BaseModel):
    code: int #自定义状态码
    msg: str #提示文字
    data: Optional[Any] = None
    # `data`：真正的数据主体；`Optional[Any]` 代表可以不传 data（比如删除成功，不需要返回数据）



# ---------------- 分页返回data结构 ----------------
class PageTodo(BaseModel): #专门给分页查询接口用的，data里面装分页信息
    total: int #全部todo总条数
    page: int  #当前页码
    page_size: int  #一页多少条
    list: List[dict] #当前页的数据数组，每条都是字典
