# 整合封装根据Token查询用户，返回用户的方法

from fastapi import Header, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_conf import get_db
from crud import users

# 整合：根据 Token 查询用户，返回用户，封装为一个工具函数方便后续接口使用
# 所需参数：
# 在前端发起请求后，后端会接收到一个请求头，里面包含Authorization字段，这个字段的值为：Bearer <token>
# 例如Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
# 这时候，FastAPI 自动从请求头中提取 Authorization 字段，作为参数传入，这里定义一个参数 authorization，类型为：str--字符串类型，设置别名为 Authorization 要与请求头中定义的相同
async def get_current_user(authorization: str = Header(..., alias="Authorization"), db: AsyncSession = Depends(get_db)):
    # 在获取token时，不能直接使用"Authorization",因为前端的请求标准写法为：Authorization: Bearer <token>
    # 所以，我们在后端使用token时，需要将token截取掉前缀"Bearer "，这里有个空格
    # 因此标准写法为：token = authorization.split(" ")[1]，这可以把"bearer <token>"中的空格去掉，然后就能返回一个列表第一个为bearer，第二个为token
    # [1]是取得列表的第二个值，即token
    # 还有一种写法
    # 将"Bearer "替换成""，即可获取token
    token = authorization.replace("Bearer ", "")
    user = await users.get_user_by_token(db, token)
    # 考虑用户不存在，则返回错误信息
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的令牌或已经过期的令牌")
    return user
