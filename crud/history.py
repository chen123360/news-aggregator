from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.history import History
from models.news import News


# 定义检查历史记录状态方法
async def is_news_history(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    query = select(History).where(History.user_id == user_id, History.news_id == news_id)
    result = await db.execute(query)
    return result.scalar_one_or_none() is not None

# 定义添加历史记录方法
async def add_history(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    history = History(user_id=user_id, news_id=news_id)
    db.add(history)
    await db.commit()
    await db.refresh(history)
    return history

# 定义获取历史记录方法，返回列表和总量
async def get_history_list(
        db: AsyncSession,
        user_id: int,
        page: int,
        page_size: int
):
    count_query = select(func.count()).where(History.user_id == user_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()
    query = select(News, History.view_time, History.id.label("history_id")).join(History, History.news_id == News.id).where(History.user_id == user_id).order_by(History.view_time.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    rows = result.all()
    return rows, total

# 定义删除历史记录方法
async def delete_history(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    query = delete(History).where(History.news_id == news_id, History.user_id == user_id)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount > 0

# 删除所有历史记录
async def remove_all_history(
        db: AsyncSession,
        user_id: int
):
    # 删单条还需要获取单条记录的id，但是清除不用，清除就是把用户id对应的历史记录直接delete就行
    stmt = delete(History).where(History.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount or 0





