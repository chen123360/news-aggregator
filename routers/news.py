# 这里写模块化路由

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud import news

# 创建 APIRouter 实例，定义 router 为实例
# 参数 prefix 是路由前缀，tags 代表的是分组名
router = APIRouter(prefix="/api/news", tags=["news"])

# 定义分类路由
# 这里是 @router，就是我们所定义的实例
@router.get("/categories")
# 根据项目需求文档，这里写两个参数，skip--跳过的记录数，默认为0，limit--返回的记录数限制，默认为100
# 定义参数 db 类型为：AsyncSession 是 SQLAlchemy 提供的异步数据库会话类
# Depends 是 FastAPI 的依赖注入系统，Depends() 的括号中应该放置依赖项，比如数据库会话对象
# get_db 是我们定义的依赖项，用于获取数据库会话对象
async def get_categories(skip: int = 0, limit: int = 100, db: AsyncSession= Depends(get_db)):
    # 调用获取新闻分类方法--news.get_categories
    categories = await news.get_categories(db, skip, limit)
    # 响应结果
    return {
        # 根据文档中的响应示例，返回对应的格式
        #
        "code": 200,
        # 返回信息
        "message": "获取新闻分类成功",
        # 返回数据
        "data": categories
    }

#定义获取新闻列表路由
@router.get("/list")
# 参数：category_id--新闻分类ID，page--当前页码，page_size--每页数量
async def get_news_list(
        # alias="categoryId"--参数别名，对应文档中的参数名
        category_id: int = Query(..., alias="categoryId"),
        page: int = 1,
        # le=100--参数最大值，这里设置最大值为100
        page_size: int = Query(10, alias="pageSize", le=100),
        db: AsyncSession = Depends(get_db)
):
    # 定义 offset 接收跳过的数量，对应形参skip
    offset = (page - 1) * page_size
    # 调用获取指定分类ID下的所有新闻，并在前面加上 await 表示异步，并赋值给 news_list
    news_list = await news.get_news_list(db, category_id, offset, page_size)
    # 调用计算总量的方法，把计算结果赋值给 total
    total = await news.get_news_count(db, category_id)
    #计算是否还有更多，只需判断（跳过的 + 当前列表里面的数量）< 总量
    # 定义 has_more 接收结果 bool 值
    has_more = (offset + len(news_list)) < total
    # 返回文档中指定格式的结果
    return {
        "code": 200,
        "message": "获取新闻列表成功",
        "data": {
            "list": news_list,
            "total": total,
            "hasMore": has_more
        }
    }

# 定义获取新闻详情路由
@router.get("/detail")
async def get_news_detail(news_id: int = Query(..., alias="id"), db: AsyncSession = Depends(get_db)):
    # 调用获取新闻详情的方法,并定义news_detail进行接收，并把用户输入的新闻ID--news_id 放入函数中
    news_detail = await news.get_news_detail(db, news_id)
    # 考虑如果用户输入的新闻ID不存在
    if not news_detail:
        raise HTTPException(status_code=404, detail="新闻不存在")
    # 调用浏览量+1的方法,定义 views_res 进行接收，并传入新闻ID--news_id
    views_res = await news.increment_news_view(db, news_detail.id)
    # 考虑如果用户输入的ID不存在
    if not views_res:
        raise HTTPException(status_code=404, detail="新闻不存在")
    # 调用获取同类新闻的方法，并定义related_news接收
    related_news = await news.get_related_news(db, news_detail.id, news_detail.category_id)
    # 返回文档中指定格式的结果
    return {
        #
        "code": 200,
        "message": "success",
        "data": {
            "id": news_detail.id,
            "title": news_detail.title,
            "content": news_detail.content,
            "image": news_detail.image,
            "author": news_detail.author,
            "publishTime": news_detail.publish_time,
            "categoryId": news_detail.category_id,
            "views": news_detail.views,
            "relatedNews": related_news
        }
    }