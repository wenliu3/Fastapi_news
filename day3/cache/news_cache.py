#新闻相关的缓存方法:新闻分类的读取和写入
# key-value
from typing import Any

from day3.config.redis_conf import get_cache_list, set_cache, get_cache_str

CATEGORIES_KEY = "news:categories"
NEWS_LIST_KEY = "news:list:{category_id}:{page}:{page_size}"
NEWS_DETAIL_KEY = "news:detail:{news_id}"
NEWS_VIEWS_KEY = "news:views:{news_id}"
NEWS_RELATED_KEY = "news:related:{category_id}:{news_id}:{limit}"
# 1.新闻类型的缓存方法
# 1.1 读取新闻类型
async def get_categories_cache():
    return await get_cache_list(CATEGORIES_KEY)
# 1.2 写入新闻类型
async def set_categories_cache(data: list[dict[str, Any]], expire: int = 4800):
    return await set_cache(CATEGORIES_KEY, data, expire)

# 2.新闻列表的缓存方法
# 2.1 获取新闻列表
# skill = (page - 1) * page_size -> page = skill // page_size + 1
async def get_news_list_cache(category_id: int, skill: int, page_size: int):
    page = skill // page_size + 1
    return await get_cache_list(NEWS_LIST_KEY.format(category_id=category_id, page=page, page_size=page_size))
# 2.2 写入新闻列表
async def set_news_list_cache(category_id: int, skill: int, page_size: int, data: list[dict[str, Any]], expire: int = 1800):
    page = skill // page_size + 1
    return await set_cache(NEWS_LIST_KEY.format(category_id=category_id, page=page, page_size=page_size), data, expire)

# 3.新闻详情的缓存方法
# 3.1 获取新闻详情
async def get_news_detail_cache(news_id: int):
    return await get_cache_list(NEWS_DETAIL_KEY.format(news_id=news_id))
# 3.2 写入新闻详情
async def set_news_detail_cache(news_id: int, data: dict[str, Any], expire: int = 3600):
    return await set_cache(NEWS_DETAIL_KEY.format(news_id=news_id), data, expire)

# 4.新闻浏览量的缓存方法
# 4.1 获取新闻浏览量
async def get_news_views_cache(news_id: int):
    return await get_cache_str(NEWS_VIEWS_KEY.format(news_id=news_id))
# 4.2 写入新闻浏览量
async def set_news_views_cache(news_id: int, data: int, expire: int = 600):
    return await set_cache(NEWS_VIEWS_KEY.format(news_id=news_id), data, expire)

# 5.新闻关联的缓存方法
# 5.1 获取新闻关联
async def get_related_news_cache(category_id: int, news_id: int, limit: int = 5):
    return await get_cache_list(NEWS_RELATED_KEY.format(category_id=category_id, news_id=news_id, limit=limit))
# 5.2 写入新闻关联
async def set_related_news_cache(category_id: int, news_id: int, data: list[dict[str, Any]], limit: int = 5, expire: int = 300):
    return await set_cache(NEWS_RELATED_KEY.format(category_id=category_id, news_id=news_id, limit=limit), data, expire)