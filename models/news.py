# 这里写数据库模型类

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Index, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String

# 定义模型类的规范
# 基类需要继承 DeclarativeBase--ORM声明式基类--用于创建数据库模型类的基类
# 数据库表模型类要继承基类
# 属性和类型需要参照数据库表定义

# 定义基类--每个子类都要继承该基类，所以定义通用的字段放在基类中
class Base(DeclarativeBase):
    # 定义创建时间
    # Mapped--ORM注解标识符--作用：映射字段，写法为 字段名: Mapped[字段类型] = mapped_column(...)
    created_at: Mapped[datetime] = mapped_column(
        # 映射字段为时间类型
        DateTime,
        # 默认值设为当前时间
        default=datetime.now(),
        comment="创建时间"
    )
    # 定义更新时间
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(),
        comment="更新时间"
    )

# 定义新闻分类表对应的模型类
# 继承基类
class Category(Base):
    # 模型类定义的表名必须与数据库表名一致，定义的字段类型也必须一致
    __tablename__ = "news_category"
    # 以下参数的解释：
    # Integer--映射的字段为整形
    # primary_key--是否是主键
    # autoincrement--是否允许自增
    # comment--对定义参数进行描述
    # String(50)--映射字段为字符串，长度不超过50
    # unique--是否唯一
    # nullable--是否为空
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="分类ID")
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="分类名称")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="排序")

    # 打印的对象可以用到 return 结果，可以看到定义参数的具体值，比如：id值，name值，排序结果
    # 如果没有，那么打印出来的是地址，而不是具体值
    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name}, sort={self.sort_order})>"

# 定义新闻模型类
class News(Base):
    __tablename__ = "news"
    # 创建索引：提升查询速度,相当于给一本书添加目录
    # 根据新闻咨询类的经验，用分类id和发布时间创建索引
    # 其中参数名--fk_news_category_idx，idx_publish_time为自定义的，是创建索引的名称
    # 后面跟的参数是表中的字段名
    __table_args__ = (
        # 使用分类id是因为他是高频查询场景
        Index('fk_news_category_idx', 'category_id'),
        # 使用发布时间是因为按发布时间排序是新闻系统的刚需
        Index('idx_publish_time', 'publish_time'),
    )
    # 对应数据库表中的字段
    # Optional--为可选的意思，字段可以为空
    # ForeignKey--外键
    # default--默认值
    # DateTime--映射字段为时间类型
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="新闻ID")
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="新闻标题")
    description: Mapped[Optional[str]] = mapped_column(String(500), comment="新闻简介")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="新闻内容")
    image: Mapped[Optional[str]] = mapped_column(String(255), comment="封面图片URL")
    author: Mapped[Optional[str]] = mapped_column(String(50), comment="作者")
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("news_category.id"), nullable=False, comment="分类ID")
    views: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="浏览量")
    publish_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="发布时间")

    def __repr__(self):
        return f"<News(id={self.id}, title='{self.title}', views={self.views})>"


