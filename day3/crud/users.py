from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from day3.models.users import User, UserToken
from day3.schemas.users import UserRequest, UserUpdateRequest
import uuid
from day3.utils.security import get_hash_password, verify_password


# 根据用户名查询用户
async def get_user_by_name(username: str, db: AsyncSession):
    result = select(User).where(User.username == username)
    user = await db.execute(result)
    return user.scalar_one_or_none()

# 创建用户
async def create_user(user_data: UserRequest, db: AsyncSession):
    hash_password = get_hash_password(user_data.password)
    user = User(username=user_data.username, password=hash_password)
    db.add( user)
    await db.commit()
    await db.refresh( user)
    return  user

# 创建Token
async def create_token(db: AsyncSession, user_id: int):
    token = str(uuid.uuid4())
    # 设置过期时间
    expire_time = datetime.now() + timedelta(days=7)
    query = select(UserToken).where(UserToken.user_id == user_id)
    result = await db.execute(query)
    user_token = result.scalar_one_or_none()
    if user_token:
        user_token.token = token
        user_token.expires_at = expire_time
    else:
        user_token = UserToken(user_id=user_id, token=token, expires_at=expire_time)
        db.add(user_token)
        await db.commit()
    return token

# 用户认证
async def authenticate_user(username: str, password: str, db: AsyncSession):
    user = await get_user_by_name(username, db)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user

# 根据Token查询用户
async def get_user_by_token(token: str, db: AsyncSession):
    query_token = select(UserToken).where(UserToken.token == token)
    result = await db.execute(query_token)
    db_token = result.scalar_one_or_none()
    if not db_token or db_token.expires_at < datetime.now():
        return None
    query_user = select(User).where(User.id == db_token.user_id)
    result = await db.execute(query_user)
    return result.scalar_one_or_none()

async def update_user(user_name: str, user_data: UserUpdateRequest, db: AsyncSession):
    # update(User).where(User.username == username).values(字段=值, 字段=值)
    # user_data 是一个Pydantic类型, 得到字典 → ** 解包
    # 没有设置值的不更新
    query = update(User).where(User.username == user_name).values(**user_data.model_dump(
        exclude_unset=True, exclude_none=True))
    result = await db.execute(query)
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="用户不存在")

    return await get_user_by_name(user_name, db)

# 修改用户密码：验证旧密码 -> 修改新密码
async def change_password(user: User, old_password: str, new_password: str, db: AsyncSession):
    if not verify_password(old_password, user.password):
        return False
    user.password = get_hash_password(new_password)
    # 更新
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return True