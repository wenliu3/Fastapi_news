from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from day3.models.favorite import Favorite
from day3.models.news import News


# 查询是否收藏新闻
async def favorite_status(news_id: int, user_id: int, db: AsyncSession):
    query = select(Favorite).where(Favorite.news_id == news_id, Favorite.user_id == user_id)
    favorite = await db.execute(query)
    return favorite.scalar_one_or_none() is not None

# 添加收藏新闻
async def add_news_favorite(news_id: int, user_id: int, db: AsyncSession):
    favorite = Favorite(news_id=news_id, user_id=user_id)
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite

# 取消收藏新闻
async def remove_news_favorite(news_id: int, user_id: int, db: AsyncSession):
    result = await db.execute(delete(Favorite).where(Favorite.news_id == news_id, Favorite.user_id == user_id))
    await db.commit()
    return result.rowcount > 0

# 获取收藏列表数据
async def favorite_list(db: AsyncSession, user_id: int, page_size: int = 10, page_num: int = 1):
    # 获取总条数
    total_query = await db.execute(select(func.count(Favorite.id)))
    total = total_query.scalar_one()
    skip = (page_num - 1) * page_size
    # 获取收藏列表
    # [(news, favorite_time, favorite_id), (news, favorite_time, favorite_id), ...]
    favorite_query = (select(News, Favorite.created_at.label("favorite_time"), Favorite.id.label("favorite_id"))
                      .join(Favorite, Favorite.news_id == News.id)
                      .where(Favorite.user_id == user_id)
                      .order_by(Favorite.created_at.desc())
                      .offset(skip).limit(page_size))
    result = await db.execute(favorite_query)
    return result.all(), total
