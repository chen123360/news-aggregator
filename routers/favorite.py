from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_conf import get_db
from models.users import User
from schemas.favorite import FavoriteCheckResponse, FavoriteAddRequest, FavoriteListResponse
from utils.auth import get_current_user
from utils.response import success_response
from crud import favorite

router = APIRouter(prefix="/api/favorite",tags=["favorite"])

# 定义检查新闻收藏状态路由
@router.get("/check")
# 在这因为需要的 news_id 在前端中为 newsId，所以在这定义别名
async def check_favorite(
        news_id: int = Query(..., alias="newsId"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    # 调用检查收藏状态的方法
    is_favorite = await favorite.is_news_favorite(db, user.id, news_id)
    # 因为 is_favorite 得到的是布尔值，只是一个结果
    # 因为要求返回的 data 是一个大括号，里面是isFavorite是 Ture 或者 Fault
    # 实例 "data" = {"isFavorite": Ture}，所以建立一个pydantic模型类
    return success_response(message="检查收藏状态成功", data=FavoriteCheckResponse(isFavorite=is_favorite))

# 定义添加新闻收藏路由
@router.post("/add")
async def add_favorite(
        # data 为请求体参数，使用我们所定义的pydantic模型类--FavoriteAddRequest
        data: FavoriteAddRequest,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    # 调用添加收藏的方法
    result = await favorite.add_news_favorite(db, user.id, data.news_id)
    return success_response(message="添加新闻收藏成功", data=result)

# 定义取消新闻收藏路由
@router.delete("/remove")
async def remove_favorite(
        news_id: int = Query(..., alias="newsId"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    # 调用取消收藏的方法
    result = await favorite.remove_news_favorite(db, user.id, news_id)
    if not result:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="收藏记录不存在")
    return success_response(message="删除收藏成功")

# 定义获取收藏新闻列表路由
@router.get("/list")
# 所需参数：对于获取收藏新闻列表，我们需要当前的用户信息，以及数据库，考虑到收藏列表可能数量很多，在这加上页码和每条页数这两个参数
# page--页码，ge=1 表示页码必须大于等于1
# page_size--每页数量，ge=1 表示每页数量必须大于等于1，le=100 表示每页数量必须小于等于100，别名为 pageSize
# user--当前用户信息
# db--数据库
async def get_favorite_list(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    # 调用获取收藏新闻列表的方法
    rows, total = await favorite.get_favorite_list(db, user.id, page, page_size)
    # 对于得到的返回结果，因为格式不对，不能直接赋值给data，所以用列表推导式进行处理
    favorite_list = [{
        # 对news进行解包，获取其中的id等属性
        **news.__dict__,
        "favorite_time": favorite_time,
        "favorite_id": favorite_id
    } for news, favorite_time, favorite_id in rows]
    # 检查是否还有更多
    has_more = total > page * page_size
    data = FavoriteListResponse(list=favorite_list, total=total, hasMore=has_more)
    return success_response(message="获取收藏列表成功", data=data)

# 定义清空收藏列表路由
@router.delete("/clear")
# 所需参数：当前用户信息，数据库
# user--当前用户信息
# db--数据库
async def clear_favorite(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    # 调用清空收藏列表的方法
    count = await favorite.remove_all_favorite(db, user.id)
    return success_response(message=f"清空了{count}条记录")

















