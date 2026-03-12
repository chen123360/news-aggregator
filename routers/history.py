from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_conf import get_db
from models.users import User
from schemas.history import HistoryAddRequest, HistoryListResponse
from utils.auth import get_current_user
from utils.response import success_response
from crud import history

router = APIRouter(prefix="/api/history", tags=["history"])

# 定义添加历史记录路由
@router.post("/add")
async def add_history(
        data: HistoryAddRequest,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user)
):
    # 调用检查历史状态的方法
    is_history = await history.is_news_history(db, user.id, data.news_id)
    if is_history:
        return {"message": "该新闻已添加过"}
    # 调用添加历史方法
    result = await history.add_history(db, user.id, data.news_id)
    return success_response(message="添加历史成功", data = result)

# 定义获取历史列表路由
@router.get("/list")
async def get_history_list(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    # 调用获取历史列表的方法
    rows, total = await history.get_history_list(db, user.id, page, page_size)
    history_list = [
        {
            **news.__dict__,
            "view_time": view_time,
            "history_id": history_id
        } for news, view_time, history_id in rows
    ]
    has_more = total > page * page_size
    data = HistoryListResponse(list=history_list, total=total, hasMore=has_more)
    return success_response(message="获取历史列表成功", data=data)

# 定义删除历史记录路由
@router.delete("/delete/{history_id}")
async def delete_history(
        history_id: int,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user)
):
    # 调用删除历史方法
    result = await history.delete_history(db, user.id, history_id)
    # 考虑如果返回结果为空的，则返回404
    if not result:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="历史记录不存在")
    return success_response(message="删除成功")

# 定义清空历史记录路由
@router.delete("/clear")
async def clear_history(
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user)
):
    # 调用清空历史方法
    count = await history.remove_all_history(db, user.id)
    return success_response(message=f"清空了{count}条记录")


