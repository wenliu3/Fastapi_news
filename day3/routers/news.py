from fastapi import APIRouter, HTTPException
from fastapi.params import Depends, Query
from sqlalchemy import null
from sqlalchemy.dialects.mssql.information_schema import views
from sqlalchemy.ext.asyncio import AsyncSession
from day3.config.db_config import get_db
from day3.crud import news, news_cache

router = APIRouter(prefix="/api/news", tags=["news"])


#接口实现流程
# 1.模块化路由>API接口规范文档
# 2.定义模型类数据库表(数据库设计文档)
# 3.在 crud文件夹里面创建文件，封装操作数据库的方法
# 4.在路由处理函数里面调用 crud 封装好的方法，响应结果
@router.get("/categories")
async def get_categories(db: AsyncSession = Depends(get_db), skill: int = 0, limit: int = 100):
    categories = await news_cache.get_categories(db, skill, limit)
    return {
        "code": 200,
        "message": "新闻分类获取成功",
        "data": categories
    }


# 思路: 处理分页规则 -> 查询新闻列表 -> 计算总量 -> 计算是否还有更多
@router.get("/list")
async def get_news_list(
        db: AsyncSession = Depends(get_db),
        category_id: int = Query(..., alias="categoryId"),
        page: int = 1,
        page_size: int = Query(10, le=100, alias="pageSize"),
):
    offset = (page - 1) * page_size
    news_list = await news_cache.get_news_list(db, category_id, offset, page_size)
    total = await news.get_news_count(db, category_id)
    hasMore = total > offset + len(news_list)
    return {
        "code": 200,
        "message": "新闻列表获取成功",
        "data": {
            "list": news_list,
            "total": total,
            "hasMore": hasMore
        }
    }


@router.get("/detail")
async def get_news_detail(
        db: AsyncSession = Depends(get_db),
        news_id: int = Query(..., alias="id")
):
    news_detail = await news_cache.get_news_detail(db, news_id)
    news_vies = await news.update_news_views(db, news_id)
    if not news_vies:
        raise HTTPException(status_code=404, detail="新闻浏览量更新失败")
    if not news_detail:
        raise HTTPException(status_code=404, detail="新闻不存在")

    related_news = await news_cache.get_related_news(db, news_detail.category_id, news_id, limit=5)
    return {
      "code": 200,
      "message": "success",
      "data": {
        "id": news_detail.id,
        "title": news_detail.title,
        "content": news_detail.content,
        "image": news_detail.image,
        "author": news_detail.author,
        "publishTime": news_detail.publish_time,
        "categoryId": news_detail.category_id,
        "views": news_detail.views,
        "relatedNews": related_news
  }
}


