from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from day3.models.news import NewsCategory, News


# 获取新闻分类
async def get_categories(db: AsyncSession, skill: int = 0, limit: int = 100):
    result = select(NewsCategory).offset(skill).limit(limit)
    categories = await db.execute(result)
    return categories.scalars().all()

# 获取新闻列表
async def get_news_list(db: AsyncSession, category_id: int, skill: int = 0, page_size: int = 10):
    result = select(News).where(News.category_id==category_id).offset(skill).limit(page_size)
    news_list = await db.execute(result)
    return news_list.scalars().all()

# 根据新闻类型找总数
async def get_news_count(db: AsyncSession, category_id: int):
    result = select(func.count(News.id)).where(News.category_id==category_id)
    total = await db.execute(result)
    return total.scalar_one()

# 获取新闻详情
async def get_news_detail(db: AsyncSession, news_id: int):
    result = select(News).where(News.id==news_id)
    detail = await db.execute(result)
    return detail.scalar_one_or_none()

# 新闻浏览量
async def update_news_views(db: AsyncSession, news_id: int):
    result = update(News).where(News.id==news_id).values(views=News.views+1)
    news_views = await db.execute(result)
    await db.commit()

    return news_views.rowcount > 0

# 获取关联的新闻
async def get_related_news(db: AsyncSession, category_id: int , news_id: int, limit: int = 5, ):
    result = select(News).where(
        News.category_id==category_id,
        News.id != news_id
    ).order_by(
        News.views.desc(),
        News.publish_time.desc()
    ).limit(limit)
    related_news = await db.execute(result)

    return [{"id": news_detail.id,
        "title": news_detail.title,
        "content": news_detail.content,
        "image": news_detail.image,
        "author": news_detail.author,
        "publishTime": news_detail.publish_time,
        "categoryId": news_detail.category_id,
        "views": news_detail.views,} for news_detail in related_news.scalars().all()]