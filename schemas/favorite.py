from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from schemas.base import NewsItemBase


# 检查是否响应结果pydantic模型类
class FavoriteCheckResponse(BaseModel):
    is_favorite: bool = Field(..., alias="isFavorite")

# 添加收藏请求体参数pydantic模型类
class FavoriteAddRequest(BaseModel):
    news_id: int = Field(..., alias="newsId")

# 对于列表里面的类，在这里规划两个类，一个是新闻模型类 + 收藏的模型类
# 对于新闻模型类，因为在浏览历史中会复用到，所以在schemas中新建base放这个模型类
class FavoriteNewsItemResponse(NewsItemBase):
    favorite_id: int = Field(..., alias="favoriteId")
    favorite_time: datetime = Field(..., alias="favoriteTime")

    # 因为要从ORM提取值，还涉及到别名和字段名要兼容，所以这里使用model_config
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )

# 收藏列表接口响应模型类
class FavoriteListResponse(BaseModel):
    list: list[FavoriteNewsItemResponse]
    total: int
    has_more: bool = Field(..., alias="hasMore")

    # 因为要从ORM提取值，还涉及到别名和字段名要兼容，所以这里使用model_config
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )
