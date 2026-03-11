# 封装对密码加密的方法

from passlib.context import CryptContext

# 定义pwd_context接收创建的密码加密上下文对象
# CryptContext--passlib 库提供的密码加密类
# schemes--指定使用的密码加密算法
# deprecated="auto"--自动处理过时的配置
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#调用哈希方法进行密码加密
def get_hash_password(password: str):
    return pwd_context.hash(password)

# 密码验证
# plain_password--明文密码
# hashed_password--密文密码
def verify_password(plain_password, hashed_password):
    #verify方法--验证密码,返回布尔值
    return pwd_context.verify(plain_password, hashed_password)