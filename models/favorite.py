# 检查用户收藏状态的模型类

from datetime import datetime

from sqlalchemy import UniqueConstraint, Index, Integer, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from models.news import News
from models.users import User

# 创建基类
class Base(DeclarativeBase):
    pass

# 创建收藏模型类
class Favorite(Base):
    __tablename__ = "favorite"
    # 创建索引
    __table_args__ = (
        # 创建唯一约束--意思是：user_id和news_id不能重复，当前新闻只能收藏一次
        UniqueConstraint("user_id", "news_id", name="user_news_unique"),
        Index("fk_favorite_user_id", "user_id"),
        Index("fk_favorite_news_id", "news_id"),
    )

    # 创建字段
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="收藏ID")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(User.id), nullable=False, comment="用户ID")
    news_id: Mapped[int] = mapped_column(Integer, ForeignKey(News.id), nullable=False, comment="新闻ID")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow(), nullable=False, comment="收藏时间")

    def __repr__(self):
        return f"<Favorite(id={self.id}, user_id={self.user_id}, news_id={self.news_id}, created_at={self.created_at})>"











