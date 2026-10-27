from typing import Optional, Any, List
from pydantic import BaseModel, Field

#BaseModel ：该类实例化后，返回python对象，Fastapi自动序列化，执行.model_dump()
# 将对象转为python字典,fastapi再把该字典转为JSON字符串发给前端

class UserRegister(BaseModel):  #用户注册-输入接口
    username:str
    password:str

class UserLogin(BaseModel):  #用户登陆-输入接口
    username: str
    password: str


class TodoCreate(BaseModel): #新增待办-输入接口
    content:str=Field(max_length=100) #限制长度，过长会报错：422校验错误

class TodoUpdate(BaseModel):  #更新待办-输入接口
    content:Optional[str]=Field(default=None,max_length=100)
    is_done:bool

class Resp(BaseModel): #统一的输出接口格式
    code:int #自定义状态码
    msg:str #提示文字
    data:Optional[Any]=None #Any是typing库里导入的类型，是类名

class PageTodo(BaseModel):  #分页筛选的输出接口格式，嵌套在上面的data里
    total:int
    page:int
    page_size:int
    list:List[dict] #List是typing库里导入的类型，是类名


