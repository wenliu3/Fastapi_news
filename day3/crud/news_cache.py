from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from day3.cache.news_cache import get_categories_cache, set_categories_cache, get_news_list_cache, set_news_list_cache, \
    get_news_detail_cache, set_news_detail_cache, get_related_news_cache, set_related_news_cache
from day3.models.news import NewsCategory, News


# 获取新闻分类
async def get_categories(db: AsyncSession, skill: int = 0, limit: int = 100):
    # 从缓存中获取数据
    categories_cache = await get_categories_cache()
    if categories_cache:
        return [NewsCategory(**item) for item in categories_cache]
    result = select(NewsCategory).offset(skill).limit(limit)
    categories = await db.execute(result)
    categories_orm = categories.scalars().all()
    # 写入缓存
    if categories_orm:
        """
        不能用该方法categories_list = [ category.__dict__ for category in categories_orm] 
        因为返回：
        {
          "id": 1,
          "name": "分类1",
          "_sa_instance_state": <sqlalchemy.engine.InstanceState object at 0x000001C...>
        }
        _sa_instance_state 是 SQLAlchemy 内部对象，不能转 JSON，不能存 Redis！
        所以用jsonable_encoder(categories_orm)
        也可以用data_news = [NewsItemBase.model_validate(item).model_dump(model="json", by_alias=False) for item in news_list]
        """
        await set_categories_cache(jsonable_encoder(categories_orm))
    return categories_orm

# 获取新闻列表
async def get_news_list(db: AsyncSession, category_id: int, skill: int = 0, page_size: int = 10):
    # 通过缓存获取新闻列表
    news_list_cache = await get_news_list_cache(category_id, skill, page_size)
    if news_list_cache:
        # return news_list_cache 要ORM对象
        return [News(**item) for item in news_list_cache]
    result = select(News).where(News.category_id==category_id).offset(skill).limit(page_size)
    news_list = await db.execute(result)
    news_orm = news_list.scalars().all()
    # 写入缓存
    if news_orm:

        await set_news_list_cache(category_id, skill, page_size, jsonable_encoder(news_orm))
    return news_orm

# 根据新闻类型找总数
async def get_news_count(db: AsyncSession, category_id: int):
    result = select(func.count(News.id)).where(News.category_id==category_id)
    total = await db.execute(result)
    return total.scalar_one()

# 获取新闻详情
async def get_news_detail(db: AsyncSession, news_id: int):
    # 通过缓存获取新闻详情
    news_detail_cache = await get_news_detail_cache(news_id)
    if news_detail_cache:
        return News(**news_detail_cache)
    result = select(News).where(News.id==news_id)
    detail = await db.execute(result)
    news_detail_orm = detail.scalar_one_or_none()
    # 写入缓存
    if news_detail_orm:
        await set_news_detail_cache(news_id, jsonable_encoder(news_detail_orm))
    return news_detail_orm

# 新闻浏览量
async def update_news_views(db: AsyncSession, news_id: int):
    result = update(News).where(News.id==news_id).values(views = News.views + 1)
    news_views = await db.execute(result)
    await db.commit()

    return news_views.rowcount > 0

# 获取关联的新闻
async def get_related_news(db: AsyncSession, category_id: int , news_id: int, limit: int = 5, ):
    # 通过缓存获取关联的
    related_news_cache = await get_related_news_cache(category_id, news_id, limit)
    if related_news_cache:
        return [News(**item) for item in related_news_cache]
    result = select(News).where(
        News.category_id==category_id,
        News.id != news_id
    ).order_by(
        News.views.desc(),
        News.publish_time.desc()
    ).limit(limit)
    related_news = await db.execute(result)
    related_news_orm = related_news.scalars().all()
    # 写入缓存
    if related_news_orm:
        await set_related_news_cache(category_id, news_id, jsonable_encoder(related_news_orm), limit)
    return related_news_orm