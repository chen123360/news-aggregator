# 配置Redis客户端
import json
from typing import Any

import redis.asyncio as redis

# 写一个变量，存上服务器的地址，万一以后地址变了，直接改地址值就行
REDIS_HOST = "localhost"
# 同理
REDIS_PORT = 6379
REDIS_DB = 0

# 创建 Redis 的连接对象
redis_client = redis.Redis(
    # Redis 服务器的主机地址
    host=REDIS_HOST,
    # Redis 端口号
    port=REDIS_PORT,
    # Redis 数据库编号，0-15
    db=REDIS_DB,
    # 是否将字节数据解码为字符串
    decode_responses=True
)

# 封装缓存的操作方法--设置和读取
# 对于读取方法，准备封装两个方法，因为存入数据之前，数据类型可能为字符串或者列表，字典
# 对于字符串，存是字符串，读也是字符串，但是对于列表或者字典来说，读就需要把它转化为字符串
# 如果列表或者字典转化为字符串，那么python就要进行二次解析，比较麻烦，所以在封装方法时，就把他序列化
# 读取：字符串
async def get_cache(key: str):
    # return await redis_client.get(key)
    # 对于get方法，它不一定能拿到对应的值
    # 所以这里用try...except...来处理
    try:
        return await redis_client.get(key)
    except Exception as e:
        print(f"获取缓存失败：{e}")
        return None

#读取：列表或者字典
async def get_json_cache(key: str):
    try:
        data = await redis_client.get(key)
        if data:
            # 如果有data，那么把他进行序列化
            return json.loads(data)
        return None
    except Exception as e:
        print(f"获取 JSON 缓存失败：{e}")
        return None

# 设置缓存
async def set_cache(
        key: str,
        value: Any,
        # 以秒为单位
        expire: int = 3600
):
    try:
        # 如果value是字典或者列表，那么就转字符再存
        if isinstance(value, (dict,  list)):
            # ensure_ascii=False，保留中文不转译
            value = json.dumps(value, ensure_ascii=False)
        await redis_client.setex(key, expire, value)
        return True
    except Exception as e:
        print(f"设置缓存失败：{e}")
        return False
