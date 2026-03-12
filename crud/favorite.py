from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.favorite import Favorite
from models.news import News


# 定义检查收藏状态方法
async def is_news_favorite(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    query = select(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(query)
    # 返回bool值，是否有收藏记录，有收藏记录则返回True，否则返回False
    return result.scalar_one_or_none() is not None

# 定义添加新闻收藏方法
async def add_news_favorite(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    # 定义 favorite 接收这个ORM对象
    favorite = Favorite(user_id=user_id, news_id=news_id)
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite

# 定义删除新闻收藏方法
async def remove_news_favorite(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    stmt = delete(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0

# 定义获取收藏新闻列表方法
# 所需参数：对于获取收藏新闻列表，我们需要用一个用户ID指明哪个用户，以及数据库，考虑到收藏列表可能数量很多，在这加上页码和每条页数这两个参数
# db--数据库
# user_id--用户ID
# page--页码
# page_size--每页数量
async def get_favorite_list(
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        page_size: int = 10
):
    # 这个函数要计算总量和获取收藏的新闻列表，对于是否还有更多，我们放在路由函数中进行处理
    # 先计算总量
    count_query = select(func.count()).where(Favorite.user_id == user_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()
    # 获取收藏的列表，用联表查询的方法，还可以对他进行排序--根据收藏时间，再分页
    # select(查询主体, 字段别名).join(联合查询的模型类, 联合查询的条件).where().order_by().offset().limit()
    # 别名：Favorite.created_at.label("favorite_time")
    # 对于新闻表和收藏表，他们都有相同的字段名：id，创建时间，所以这里在联表查询中，可以设置别名
    query = select(News, Favorite.created_at.label("favorite_time"), Favorite.id.label("favorite_id")).join(Favorite, Favorite.news_id == News.id).where(Favorite.user_id == user_id).order_by(Favorite.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    rows = result.all()
    return rows, total

# 定义清空收藏列表方法
# 所需参数：对于清空收藏列表，我们需要用一个用户ID指明当前用户清空收藏，以及数据库
# db--数据库
# user_id--用户ID
async def remove_all_favorite(
        db: AsyncSession,
        user_id: int
):
    stmt = delete(Favorite).where(Favorite.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    # 对于返回结果，我们还需要定义一个返回的删除数量
    return result.rowcount or 0




