from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from schemas.base import NewsItemBase


# 添加历史请求体参数pydantic模型类
class HistoryAddRequest(BaseModel):
    news_id: int = Field(..., alias="newsId", description="新闻ID")

# 在前面实现获取收藏列表时，我们定义了新闻模型类，这里进行复用，继承里面的字段
class HistoryNewsItemResponse(NewsItemBase):
    view_time: datetime = Field(..., alias="viewTime", description="浏览时间")
    history_id: int = Field(..., alias="historyId", description="历史ID")

    # 因为要从ORM提取值，还涉及到别名和字段名要兼容，所以这里使用model_config
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )

# 历史列表接口响应模型类
class HistoryListResponse(BaseModel):
    list: list[HistoryNewsItemResponse]
    total: int
    has_more: bool = Field(..., alias="hasMore", description="是否有更多")

    # 因为要从ORM提取值，还涉及到别名和字段名要兼容，所以
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )