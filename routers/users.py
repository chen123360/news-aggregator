from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_conf import get_db
from models.users import User
from schemas.users import UserRequest, UserAuthResponse, UserInfoResponse, UserUpdateRequest, UserChangePasswordRequest
from crud import users
from utils.response import success_response
from utils.auth import get_current_user

router = APIRouter(prefix="/api/user",tags=["users"])

# 用户注册
# 因为接口类型为--post，所以用户信息用请求体定义，写在schemas的users中
@router.post("/register")
# 所需参数：
# 请求体参数 user_data--用户信息，类型为：UserRequest--pydantic模型类
# 数据库会话对象 db--数据库会话对象，类型为：AsyncSession--SQLAlchemy的异步数据库会话类
async def register(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    # 调用查询是否存在的用户方法，把user_data.username--用户名传入方法中
    existing_user = await users.get_user_by_username(db, user_data.username)
    # 考虑如果有用户存在，则返回错误信息
    if existing_user:
        # 抛出HTTPException异常，status_code--状态码，detail--错误信息
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户已存在")
    # 调用创建用户的方法，把user_data--用户信息传入方法中
    user = await users.create_user(db, user_data)
    # 在创建完用户之后，调用生成访问令牌方法，把创建好的user.id--用户ID传入方法中
    token = await users.create_token(db, user.id)
    # 响应结果
    # return {
    #     "code": 200,
    #     "message": "注册成功",
    #     "data": {
    #         "token": token,
    #         "userInfo": {
    #             "id": user.id,
    #             "username": user.username,
    #             "bio": user.bio,
    #             "avatar": user.avatar
    #         }
    #     }
    # }
    # 上面的响应结果太长，所以使用封装的响应结果方法
    # 首先定义工具函数 success_response()--在 utils软件包中创建response去封装的响应结果方法
    # 然后对于返回对象 data，它需要接收一个有结构的对象，在这里定义对应的pydantic响应模型类
    # 调用 UserAuthResponse函数，把生成的访问令牌和用户信息传入方法中，得到返回的信息，再定义response_data接收以当前的访问令牌和用户信息返回的数据
    # model_validate()--作用：将一个ORM对象转换为pydantic模型实例，提取对应的属性值
    response_data = UserAuthResponse(token = token, userInfo = UserInfoResponse.model_validate(user))
    return success_response(message="注册成功", data=response_data)

# 用户登录
@router.post("/login")
# 所需参数：
# 对于用户登录来说，它需要使用到登录的用户名和密码，可以复用注册时定义的请求体参数--用户信息，还需要数据库参与，因为登录时需要验证用户名、密码在数据库当中对不对
# 请求体参数 user_data--用户信息，类型为：UserRequest--pydantic模型类
# 数据库会话对象 db--数据库会话对象，类型为：AsyncSession--SQLAlchemy的异步数据库会话类
async def login(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    # 调用验证用户名和密码方法，传入数据库和对应的用户名和密码
    user = await users.authenticate_user(db, user_data.username, user_data.password)
    # 考虑用户不存在，则返回错误信息
    # 具体的业务信息还是需要自己抛出异常，全局异常处理器只是捕获异常，返回错误信息
    # 如果没有抛出异常这一步，就会执行下面的生产令牌，程序可能会崩溃
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    #调用生成访问令牌方法
    token = await users.create_token(db, user.id)
    #响应结果
    response_data = UserAuthResponse(token = token, userInfo = UserInfoResponse.model_validate(user))
    return success_response(message="登录成功", data=response_data)

# 获取用户信息
@router.get("/info")
# 对于封装的工具函数，在这不直接调用，而是通过依赖注入的方式去使用
# 通过依赖注入的方式，FastAPI会暂停函数get_user_info，直到它依赖的 get_current_user 函数返回一个结果，然后继续执行 get_user_info 函数
async def get_user_info(user: User = Depends(get_current_user)):
    # 响应结果
    return success_response(message="获取用户信息成功", data=UserInfoResponse.model_validate(user))

# 修改用户信息
@router.put("/update")
# 参数要包含：用户输入的 + 验证 Token 的 + db（调用更新方法）
async def update_user_info(user_data: UserUpdateRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # 调用更新用户信息方法
    user = await users.update_user(db, user.username, user_data)
    # 响应结果
    return success_response(message="修改用户信息成功", data=UserInfoResponse.model_validate(user))

# 修改密码
@router.put("/password")
# 所需参数：对于修改密码来说，它需要使用到旧密码和新密码，并且他还需要验证token--是否为登录状态，登录才能修改，还需要数据库参与，因为修改密码时需要验证旧密码对不对
# password_data: UserChangePasswordRequest--新旧密码，类型为：UserChangePasswordRequest--pydantic模型类，模型类中有旧密码和新密码
# user: User = Depends(get_current_user)--验证 Token 的，返回当前用户信息给user
# db: AsyncSession = Depends(get_db)--数据库会话对象，类型为：AsyncSession--SQLAlchemy的异步数据库会话类
async def update_password(password_data: UserChangePasswordRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # 调用修改密码方法
    res_change_pwd = await users.change_password(db, user, password_data.old_password, password_data.new_password)
    if not res_change_pwd:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="修改密码失败，请稍后再试")
    # 响应结果
    return success_response(message="修改密码成功")












