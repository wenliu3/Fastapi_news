from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from day3.config.db_config import get_db
from day3.crud.users import get_user_by_name, create_user, create_token, authenticate_user, update_user, change_password
from day3.models.users import User
from day3.schemas.users import UserRequest, UserAuthResponse, UserInfoResponse, UserUpdateRequest, UserPasswordRequest
from day3.utils.auth import get_current_user
from day3.utils.respon import success_response

router = APIRouter(prefix="/api/user", tags=["users"])

@router.post("/register")
async def register(users: UserRequest, db: AsyncSession = Depends(get_db)):
    # 注册逻辑:验证用户是否存在->创建用户->生成Token->响应结果
    user_name = await get_user_by_name(users.username, db)
    if user_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户已存在")
    user = await create_user(users, db)
    token = await create_token(db, user.id)
#     return {
#   "code": 200,
#   "message": "注册成功",
#   "data": {
#     "token": token,
#     "userInfo": {
#       "id": user.id,
#       "username": user.username,
#       "bio": user.bio,
#       "avatar": user.avatar,
#     }
#   }
# }
    response_data = UserAuthResponse(token=token, userInfo=UserInfoResponse.model_validate(user))
    return success_response(message="注册成功", data=response_data)

@router.post("/login")
async def login(users: UserRequest, db: AsyncSession = Depends(get_db)):
    # 登录逻辑:验证用户是否存在->生成Token->响应结果
    user = await authenticate_user(users.username, users.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
    token = await create_token(db, user.id)
    response_data = UserAuthResponse(token=token, userInfo=UserInfoResponse.model_validate(user))
    return success_response(message="登录成功", data=response_data)

# 查Token查用户->封装crud->功能整合成一个工具函数->路由导入使用:依赖注入
@router.get("/info")
async def info(user: User = Depends(get_current_user)):
    return success_response(message="获取用户信息成功", data=UserInfoResponse.model_validate(user))

# 修改用户信息
@router.put("/update")
async def update_info(
        user_data: UserUpdateRequest,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user)
):
    user = await update_user(user.username, user_data, db)
    return success_response(message="修改用户信息成功", data=UserInfoResponse.model_validate(user))

# 修改密码
@router.put("/password")
async def update_password(
        user_password: UserPasswordRequest,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user)
):
    if not await change_password(user, user_password.old_password, user_password.new_password, db):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="密码错误")
    return success_response(message="修改密码成功")