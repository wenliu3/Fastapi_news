from fastapi import FastAPI

app = FastAPI()

@app.middleware("http")
async def middleware(request, call_next):
    print("中间件1开始执行")
    response = await call_next(request)
    print("中间件1结束执行")
    return response

@app.middleware("http")
async def middleware2(request, call_next):
    print("中间件2开始执行")
    response = await call_next(request)
    print("中间件2结束执行")
    return response

@app.get("/")
async def main():
    return {"message": "Hello World"}