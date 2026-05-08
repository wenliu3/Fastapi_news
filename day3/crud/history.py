from datetime import datetime

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from day3.models.history import History
from day3.models.news import News


# 添加历史记录
async def add_new_history(db: AsyncSession, user_id: int, news_id: int):
    result = await db.execute(select(History).where(History.user_id == user_id, History.news_id == news_id))
    history = result.scalar_one_or_none()
    if history:
        history.view_time = datetime.now()
        await db.commit()
        await db.refresh(history)
        return history
    history = History(user_id=user_id, news_id=news_id, view_time=datetime.now())
    db.add(history)
    await db.commit()
    await db.refresh(history)
    return history

# 获取历史记录列表
async def get_history_list(db: AsyncSession, user_id: int, page: int = 1, page_size: int = 10):
    # 获取总条数
    total_query = select(func.count()).where(History.user_id == user_id)
    total = await db.execute(total_query)
    # 获取列表
    skip = (page - 1) * page_size
    history_query = (select(News, History.view_time, History.id.label("history_id"))
                     .join(History, History.news_id == News.id)
                     .where(History.user_id == user_id)
                     .order_by(History.view_time.desc())
                     .offset(skip).limit(page_size))

    history_list = await db.execute(history_query)
    return history_list.all(), total.scalar_one()

# 删除单条历史记录
async def delete_history(db: AsyncSession, user_id: int, news_id: int):
    result = await db.execute(delete(History).where(History.news_id == news_id, History.user_id == user_id))
    await db.commit()
    return result.rowcount > 0

# 删除所有历史记录
async def clear_history(db: AsyncSession, user_id: int):
    result = await db.execute(delete(History).where(History.user_id == user_id))
    await db.commit()
    return result.rowcount

