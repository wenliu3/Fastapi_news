from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from day3.config.db_config import get_db
from day3.crud.history import add_new_history, get_history_list, delete_history, clear_history
from day3.models.users import User
from day3.schemas.history import HistoryAddRequest, HistoryRequest, HistoryListResponse
from day3.utils.auth import get_current_user
from day3.utils.respon import success_response

router = APIRouter(prefix="/api/history", tags=["history"])

@router.post("/add")
async def add_history(add_history_request: HistoryAddRequest,
                      user: User = Depends(get_current_user),
                      db: AsyncSession = Depends(get_db)):
    history = await add_new_history(db, user.id, add_history_request.news_id)
    return success_response(message="添加成功", data=HistoryRequest.model_validate(history))

@router.get("/list")
async def history_list(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, alias="pageSize", le=100, ge=1),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    history, total = await get_history_list(db, user.id, page, page_size)
    data = [{
        **news.__dict__,
        "view_time": view_time,
        "history_id": history_id
    } for news, view_time, history_id in history]
    has_more = total > page * page_size
    return success_response(message="获取成功", data=HistoryListResponse(list=data, total=total, hasMore=has_more))

@router.delete("/delete/{news_id}")
async def get_delete_history(
        news_id: int,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    if not await delete_history(db, user.id, news_id):
        raise HTTPException(status_code=400, detail="删除失败")
    return success_response(message="删除成功")

@router.delete("/clear")
async def get_clear_history(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await clear_history(db, user.id)
    return success_response(message=f"清空成功{result}条记录")