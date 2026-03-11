# 这里写数据库的连接及配置

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

# 定义数据库 URL
ASYNC_DATABASE_URL = "mysql+aiomysql://root:lslwc0406@localhost:3306/news_app?charset=utf8mb4"

# 创建异步引擎
async_engine = create_async_engine(
    # 使用定义好的数据库URL
    ASYNC_DATABASE_URL,
    # echo 代表是否输出sql日志
    echo=True,
    # 设置连接池中保持的持久连接数
    pool_size=10,
    # 设置连接池允许创建的额外连接数
    max_overflow=20,
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    # 绑定数据库引擎
    bind=async_engine,
    # 指定会话类
    class_=AsyncSession,
    # 提交后会话不会过期，不会重新查询数据库
    expire_on_commit=False,
)

# 依赖项，用于获取数据库会话
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            # 返回数据库会话给路由处理函数
            yield session
            # 提交事物
            await session.commit()
        except:
            # 如果有异常，就进行回滚
            await session.rollback()
            raise
        finally:
            # 关闭会话
            await session.close()