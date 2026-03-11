import uuid
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import User, UserToken
from schemas.users import UserRequest, UserUpdateRequest
from utils import security

# 在数据库中根据用户名查询用户
# 所需参数：
# db--数据库会话对象
# username--用户名
async def get_user_by_username(db: AsyncSession, username: str):
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    return result.scalars().one_or_none()

# 创建用户
# 所需参数：
# db--数据库会话对象
# user_data--用户数据，为pydantic类型的请求体参数
async def create_user(db: AsyncSession, user_data: UserRequest):
    # 密码加密处理
    hashed_password = security.get_hash_password(user_data.password)
    # 创建用户user，用User模型类把用户输入的用户名和密码赋予user
    user = User(username=user_data.username, password=hashed_password)
    db.add(user)
    await db.commit()
    # 从数据库读回最新的user--刷新用户数据
    await db.refresh(user)
    return user

# 生成 Token
# 生成 Token + 设置过期时间 -> 查询数据库当前用户是否有 Token -> 有：更新；没有：添加
# 所需参数：同样要数据库的参与，并且要根据对应的用户ID来生成对应的 Token
# db--数据库会话对象
# user_id--用户ID
async def create_token(db: AsyncSession, user_id: int):
    # 对于如何生成token，我们在这使用uuid--生成唯一标识符，uuid4--生成随机的uuid，然后转换为字符串并赋值给token
    token = str(uuid.uuid4())
    # 设置过期时间 = 当前时间 + 7天
    # timedelta--返回一个时间长度
    # 全量写法:timedelta(days=7, hours=2, minutes=30, seconds=10)--解释为7天2小时30分10秒过期
    expires_at = datetime.now() + timedelta(days=7)
    # 在用户令牌表的模型类中查询数据库当前用户是否有 Token，条件为用户令牌的ID等于当前用户ID
    query = select(UserToken).where(UserToken.user_id == user_id)
    # 执行查询
    result = await db.execute(query)
    # 获取结果
    user_token = result.scalars().one_or_none()
    #判断有无，然后进行对应操作
    if user_token:
        # 更新
        user_token.token = token
        # 设置过期时间
        user_token.expires_at = expires_at
    else:
        # 添加
        user_token = UserToken(user_id=user_id, token=token, expires_at=expires_at)
        # 添加到数据库
        db.add(user_token)
        # 提交数据库
        await db.commit()
    return token

# 验证用户名和密码
# 所需参数：对于这个方法，数据库是必须的，要去数据库验证。用户名和密码也需要
# db--数据库会话对象
# username--用户名
# password--密码
async def authenticate_user(db: AsyncSession, username: str, password: str):
    # 调用在数据库中根据用户名查询用户方法，返回一个对应输入用户名的用户，用user接收
    user = await get_user_by_username(db, username)
    # 判断用户是否存在，如果不存在，则返回None
    if not user:
        return None
    # 如果存在，则验证密码
    if not security.verify_password(password, user.password):
        return None
    return  user

# 根据Token查询用户：验证 Token -> 查询用户
# 因为后续接口会复用这个功能，所以把它整合到一个工具函数里面
async def get_user_by_token(db: AsyncSession, token: str):
    # 在用户令牌的模型类中，筛选出根据输入的令牌等于用户令牌模型类中的用户令牌的记录
    query = select(UserToken).where(UserToken.token == token)
    result = await db.execute(query)
    # 定义db_token接收获取到的记录，要么是一条，要么是None
    db_token = result.scalars().one_or_none()
    # 判断对应令牌的记录是否存在或者这个记录的令牌是否过期
    # expires_at--过期时间
    if not db_token or db_token.expires_at < datetime.now():
        return None
    # 根据用户ID查询用户
    query = select(User).where(User.id == db_token.user_id)
    # 执行查询
    result = await db.execute(query)
    return result.scalars().one_or_none()

# 更新用户信息：验证用户名 -> 获取用户 -> 更新用户 -> 检查是否命中 -> 返回更新后的用户
# 所需参数：对于更新用户信息，需要数据库的参与，并且要根据对应的用户名来更新用户信息，所以需要用户名，你更新的信息也需要，所以加上用户数据
# db--数据库会话对象
# username--用户名
# user_data--用户数据，为pydantic类型的请求体参数
async def update_user(db: AsyncSession, username: str, user_data: UserUpdateRequest):
    # update(User).where(User.username == username).values(字段=值, 字段=值)
    # user_data 是一个Pydantic类型，得到字段 -> ** 解包
    # model_dump()--把Pydantic类型转换成字典
    # 同时考虑没有设置值的不更新，在model_dump()中可以设置参数exclude_unset=True和exclude_none=True实现
    query = update(User).where(User.username == username).values(**user_data.model_dump(
        exclude_unset= True,
        exclude_none= True
    ))
    # 更新之后需要检查是否更新成功，所以这里需要定义一个变量result接收execute的结果
    result = await db.execute(query)
    await db.commit()
    # 检查更新，如果命中行数为零，那么代表更新失败，抛出404异常
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="用户不存在")
    # 调用在数据库中根据用户名查询用户函数，获取一下更新后的用户
    updated_user = await get_user_by_username(db, username)
    return updated_user

# 修改密码:验证旧密码 -> 新密码加密 -> 修改密码
# 所需参数：对于修改密码，数据库是必须的，并且要验证token查询是否为登录状态，并返回登录的用户信息，还需要旧密码和新密码
# db--数据库会话对象
# user--登录的用户信息
# old_password--旧密码
# new_password--新密码
async def change_password(db: AsyncSession, user: User, old_password: str, new_password: str):
    # 如果旧密码验证失败，则返回False
    if not security.verify_password(old_password, user.password):
        return  False
    # 新密码加密
    hashed_new_pwd = security.get_hash_password(new_password)
    # 把加密的新密码赋给user对象中的密码字段
    user.password = hashed_new_pwd
    # 这里不是真的去创建一个对象，表示由sqlalchemy真正的去接管了user这个对象，确保commit可以真的提交到数据库
    # 规避 session 过期或关闭导致的不能提交的问题
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return True



