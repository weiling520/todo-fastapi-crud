"""
前端传JSON字符串 → FastAPI解析 → Pydantic输入模型校验 → 取出字段构造ORM对象→ ORM通过Session add/commit → 写入MySQL存数据
                                                                 ↓查询回来
MySQL查出一行数据 → ORM对象 → Pydantic输出模型→ 字典 → JSON字符串 → 返回前端
"""