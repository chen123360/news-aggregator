# 这里写数据库的操作方法
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update

from cache.news_cache import get_cached_categories, set_cache_categories, set_cache_news_list, get_cache_news_list
from models.news import Category, News
from schemas.base import NewsItemBase


# 封装新闻分类查询方法，处理分页规则
# 所需参数有：db数据库会话形参，skip--跳过的记录数，默认为0，limit--返回的记录数限制，默认为100
# 参数：db数据库会话形参，作用：使用execute执行select，根据习惯把db放在第一个形参位置
async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100):

    # 先尝试从缓存中获取数据，并定义cached_categories接收
    cached_categories = await get_cached_categories()
    if cached_categories:
        return cached_categories

    # 进行查询语句，并用stmt接收
    # select(模型类)：对于封装分类查询方法，把 Category 新闻分类表对应模型类传入select中
    # 后跟offset(skip)：跳过skip条记录，limit(limit)--返回的记录数限制，这两个配合在一起使用
    stmt = select(Category).offset(skip).limit(limit)
    # 异步执行数据库查询
    # await: 等待数据库响应（非阻塞式等待）
    # db.execute(stmt): 将构建好的 SQL 语句发送到数据库执行
    # result: 接收数据库返回的 Result 对象，因为返回的对象包含结果集游标，需进一步处理才能获取实际数据，所以我们在这定义result去接收
    result = await db.execute(stmt)
    # 对result进行提出所有数据并返回所有数据
    # return result.scalars().all()

    # 定义categories接收所有数据，接收的是ORM结果
    categories = result.scalars().all()

    # 写入缓存
    if categories:
        categories = jsonable_encoder(categories)
        # 调用写入缓存的方法
        await set_cache_categories(categories)
    # 返回数据
    return  categories

# 封装新闻列表查询方法，获取所有新闻
# 所需参数有：
# db--数据库会话形参，从数据库中获取所有新闻
# category_id--新闻分类ID，要根据新闻分类ID查询对应新闻
# skip--跳过的记录数，根据新闻ID查询到对应新闻时，要考虑跳过了多少条新闻，初始我们默认为0
# limit--返回的记录数限制，对于返回的新闻，我们需要对其进行限制，不能有太多条，这里我们默认为100
async def get_news_list(db: AsyncSession, category_id: int = 0, skip: int = 0 , limit: int = 10):
    # 先尝试从缓存获取新闻列表
    # 调用获取新闻列表缓存的方法
    # 对于页码参数，在当前函数中只有跳过数和每页数量，所以我们推到页码公式
    # skip = (页码 - 1) * 每页数量
    # 页码 = 跳过的记录数 // 每页数量 +1
    page = skip // limit + 1
    cached_list = await get_cache_news_list(category_id, page, limit)
    # 如果有数据就返回
    if cached_list:
        # 不是直接返回cached_list，而是返回ORM结果
        # 因为cached_list是从缓存中读出来的，他是JSON数据格式，而return应该返回ORM格式，所以这里需要转换成ORM结果
        # 这里使用列表推导式，将JSON数据转换成ORM结果
        return [News(**item) for item in cached_list]
    # 查询的是指定分类下的所有新闻，所以我们选择 select(News)--筛选新闻表对于的模型类
    # 用where(News.category_id == category_id)--筛选出指定分类ID下的新闻
    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    # return result.scalars().all()
    news_list = result.scalars().all()
    # 调用写入缓存的方法
    if news_list:
        # 把ORM数据转换为字典才能写入缓存
        # 转换思路：ORM -> Pydantic -> 字典
        # 在这里转化为Pydantic时，这个模型类考虑到前面写过新闻模型类，所以这里使用NewsItemBase
        # 这里使用model_dump()方法，将Pydantic数据转换为字典，参数by_alias=False表示不使用别名，因为在缓存中存储数据时，这是给后端用的，我们不希望使用别名
        news_data = [NewsItemBase.model_validate(item).model_dump(mode="json", by_alias=False) for item in news_list]
        # 调用写入缓存的方法
        await set_cache_news_list(category_id, page, limit, news_data)
    return news_list

# 封装计算新闻总量方法
# 所需参数有：
# db--数据库会话形参，从数据库中获取所有新闻
# category_id--新闻分类ID，要根据新闻分类ID查询对应分类的新闻，才能获取对应分类的新闻数量
async def get_news_count(db: AsyncSession, category_id: int = 0):
    # 查询指定分类下的新闻数量--这里使用func.count()--统计指定字段的数量，括号中填写字段名News.id，因为新闻的ID是唯一的，所以ID数等于总量数，所以这里使用News.id就能统计新闻数量
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)
    # scalar_one表示只返回一个数据，不然会报错
    return result.scalar_one()

# 封装查询指定新闻详情方法，获取指定新闻ID的新闻详情
# 所需参数有：
# db--数据库会话形参，从数据库中获取指定新闻ID的详情
# news_id--新闻ID，根据新闻ID查询对应新闻的详情
async def get_news_detail(db: AsyncSession, news_id: int):
    # 获取指定新闻ID的详情，所以选择 select(News)--筛选新闻表对应的模型类
    # 用where(News.id == news_id)--筛选出指定新闻ID的详情
    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    # scalar_one_or_none表示返回一个数据，如果用户指定的news_id没有与News_id相等的那么返回的数据不存在，则返回None
    return result.scalar_one_or_none()

# 封装浏览量 + 1的方法
# 所需参数有：
# db--数据库会话形参，从数据库中更新指定新闻ID的浏览量
# news_id--新闻ID，根据新闻ID更新对应新闻的浏览量
async def increment_news_view(db: AsyncSession, news_id: int):
    # 更新指定新闻ID的浏览量，所以选择 update(News)--更新新闻表对应的模型类
    # 用where(News.id == news_id)--筛选出指定新闻ID的新闻
    # values--用于指定哪些字段要更新成什么值，用values(views=News.views + 1)--更新浏览量字段的值，将浏览量字段的值+1
    stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
    result = await db.execute(stmt)
    # 稳妥起见在更新完就进行提交操作
    # 因为对于更新来说，更新操作是数据库会话会话对象，所以这里需要立刻提交，因为在数据库配置中是处理完所有事物再提交
    await db.commit()
    # 对于数据库的更新操作我们需要检查数据库是否真的命中数据，如果命中，则返回Ture，否则Fault
    # 所以我们在这里使用 rowcount--可以获取到命中的行数，如果提交成功了，那么它会大于0
    return result.rowcount > 0

# 封装获取同类新闻的方法
# 所需参数有：
# db--数据库会话形参，从数据库中获取同类新闻
# news_id--新闻ID，根据新闻ID获取当前新闻
# category_id--新闻分类ID，根据新闻分类ID获取同类新闻
# 使用形参 limit 限制同类新闻只显示五条
async def get_related_news(db: AsyncSession, news_id: int, category_id: int, limit: int = 5):
    # 获取同类新闻，所以选择 select(News)--筛选新闻表对应的模型类
    # 用where(News.category_id == category_id, News.id != news_id)--筛选出指定新闻分类ID的新闻，并除去当前新闻
    # order_by 排序 -> 根据浏览量和发布时间排序，推荐前五条同类新闻
    # News.views默认是升序排，所以这里使用News.views.desc()为降序排
    stmt = select(News).where(News.category_id == category_id, News.id != news_id).order_by(News.views.desc(), News.publish_time.desc()).limit(limit)
    result = await db.execute(stmt)
    # return result.scalars().all()
    # 如果使用return result.scalars().all()--返回所有数据，这个数据在路由中有很多字段，返回的数据很冗杂
    # 我们只需要核心数据，比如新闻ID，新闻标题，新闻内容，新闻图片，新闻作者，新闻发布时间，新闻分类ID，新闻浏览量
    # 所以这里转换成字典，使用列表推导式
    related_news = result.scalars().all()
    # 列表推导式 推导出新闻的核心数据，然后再return
    # 定义一个临时变量名--news_detail，就是 for 循环的变量名，他只是把for写在后面
    return [{
        "id": news_detail.id,
        "title": news_detail.title,
        "content": news_detail.content,
        "image": news_detail.image,
        "author": news_detail.author,
        "publishTime": news_detail.publish_time,
        "categoryId": news_detail.category_id,
        "views": news_detail.views
    } for news_detail in related_news]




