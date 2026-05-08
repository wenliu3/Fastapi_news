from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from day3.config.db_config import get_db
from day3.crud.favorite import favorite_status, add_news_favorite, remove_news_favorite, favorite_list, \
    clear_all_favorite
from day3.models.users import User
from day3.schemas.favorite import IsFavorite, FavoriteAddRequest, FavoriteListResponse
from day3.utils.auth import get_current_user
from day3.utils.respon import success_response

router = APIRouter(prefix="/api/favorite", tags=["favorite"])

@router.get("/check")
async def check_favorite(
        news_id: int = Query(..., alias = "newsId"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    is_fav = await favorite_status(news_id, user.id, db)
    return success_response(message="获取收藏状态成功", data=IsFavorite(isFavorite=is_fav))

@router.post("/add")
async def add_favorite(
        data: FavoriteAddRequest,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await add_news_favorite(data.news_id, user.id, db)
    return success_response(message="收藏成功", data=result)

@router.delete("/remove")
async def remove_favorite(
        news_id: int = Query(..., alias = "newsId"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    if not await remove_news_favorite(news_id, user.id, db):
        raise HTTPException(status_code=404, detail="取消收藏失败")
    return success_response(message="取消收藏成功")

# 获取收藏列表
@router.get("/list")
async def get_favorite_list(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, alias="pageSize", le=100, ge=1),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    fav_list,  total = await favorite_list(db, user.id, page_size, page)
    data = [{**news.__dict__,
         "favorite_time": favorite_time,
         "favorite_id": favorite_id} for news, favorite_time, favorite_id in fav_list]
    has_more = total > page * page_size
    return success_response(message="获取收藏列表成功", data=FavoriteListResponse(list=data, total=total, hasMore=has_more))

@router.delete("/clear")
async def clear_favorite(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await clear_all_favorite(db, user.id)
    return success_response(message=f"清空成功{result}收藏")

