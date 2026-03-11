# 放 pydantic 类型，做数据类型校验

from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


# 定义请求体参数--用户信息
# 只需要定义注册所需参数--用户名，密码，在写登录路由时也能复用这个请求体参数
class UserRequest(BaseModel):
    username: str
    password: str

# 创建响应数据模型类
# 创建时，把 user_info 对应的类分为两个类创建：基础类 + Info类(id、用户名)
# 基础类
class UserInfoBase(BaseModel):
    # 对于基础类的参数，考虑到在更新用户信息时可以复用基础类，因为更新用户信息时只能更新：昵称、头像、性别、个人简介
    # 所以在这设置可选参数：昵称、头像、性别、个人简介，并设置默认值 None
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")

# Info类，继承基础类，用于完整的用户信息响应
class UserInfoResponse(UserInfoBase):
    # 对于Info类，只需要添加id、用户名
    id: int
    username: str
    # 模型类配置
    # 对于 pydantic 模型类来说，不能识别 ORM 对象
    # 所以这里需要设置 from_attributes=True，允许从ORM对象属性中取值
    model_config = ConfigDict(
        from_attributes=True
    )

# 对于响应结果的 data，我们在这定义一个pydantic响应模型类去写data的结构
# 所需参数：
# token--访问令牌
# user_info--用户信息，类型为 UserInfoResponse--pydantic模型类，设置对应别名为 userInfo
class UserAuthResponse(BaseModel):
    token: str
    user_info: UserInfoResponse = Field(..., alias="userInfo")
    # 同样进行模型类配置，便于识别ORM对象属性
    model_config = ConfigDict(
        # populate_by_name 的作用为：如果字段名与属性名不一致，则使用字段名作为属性名
        populate_by_name=True,
        # 允许从ORM对象属性中取值
        from_attributes=True
    )

# 更新用户信息的模型类
class UserUpdateRequest(BaseModel):
    nickname: str = None
    avatar: str = None
    gender: str = None
    bio: str = None
    phone: str = None

# 修改密码模型类
class UserChangePasswordRequest(BaseModel):
    old_password: str = Field(..., alias="oldPassword", description="旧密码")
    new_password: str = Field(..., min_length=6, alias="newPassword", description="新密码")

