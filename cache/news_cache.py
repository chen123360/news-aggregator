# 新闻相关的缓存方法：新闻分类的读取和写入
from typing import List, Dict, Any, Optional

from config.cache_conf import get_json_cache, set_cache

# 因为Redis是通过键值对的方式进行存储的，所以这里定义一个新闻分类的缓存key，缓存的key是唯一的
CATEGORIES_KEY = "news:categories"
# 定义新闻列表的缓存key
NEWS_LIST_PREFIX = "news:list:"

# 封装获取新闻分类缓存的方法
async def get_cached_categories():
    # 对于获取新闻分类列表，我们有很多个分类，每一个分类都是字典，应该去使用读取列表或字典的方法
    return await get_json_cache(CATEGORIES_KEY)

# 写入新闻分类缓存的方法
# 所需参数：缓存的数据、过期时间
# data: 新闻数据为列表类型，列表中是字典，字典中key是str类型，value是任意类型
# expire: 过期时间
# 经验：数据越稳定，缓存越持久
# 对于分类或者配置来说默认为两小时（7200秒）
# 如果是列表数据，则默认十分钟（600秒）
# 如果是详情数据，则默认三十分钟（1800秒）
# 如果是验证码，则默认两分钟（120秒）
# 这可以避免所有的key同时过期，引起雪崩
async def set_cache_categories(data: List[Dict[str, Any]], expire: int = 7200):
    # 调用设置缓存的方法并返回
    return await set_cache(CATEGORIES_KEY, data, expire)

# 定义新闻列表的写入缓存方法
# 对于这个key，我们设置为 key = news_list:分类id:页码:每页数量
# 所以这里的参数我们考虑：分类id，页码，每页数量，因为我们是新闻列表，所以还需要列表数据，过期时间
async def set_cache_news_list(
        category_id: Optional[int],
        page: int,
        size: int,
        news_list: List[Dict[str, Any]],
        expire: int = 1800
):
    # 对于分类id来说，考虑为可选参数，有的新闻可能没有分类id，所以对他进行提前处理
    # 如果有分类id，那么就使用分类id，没有就使用all
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_PREFIX}{category_part}:{page}:{size}"
    # 调用封装的Redis的设置方法，存新闻列表缓存
    return await set_cache(key, news_list, expire)

# 定义读取新闻列表缓存的方法
async def get_cache_news_list(
        category_id: Optional[int],
        page: int,
        size: int
):
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_PREFIX}{category_part}:{page}:{size}"
    return await get_json_cache(key)











