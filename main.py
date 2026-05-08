from fastapi import FastAPI
from day3.routers import news, users, favorite
from fastapi.middleware.cors import CORSMiddleware

from day3.utils.exception_handlers import register_exception_handlers

app = FastAPI()
# 异常处理
register_exception_handlers(app)

# 跨域问题配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许的源
    allow_credentials=True, # 允许携带cookie
    allow_methods=["*"], # 允许的请求方法
    allow_headers=["*"], # 允许的请求头
)
@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(news.router)
app.include_router(users.router)
app.include_router(favorite.router)