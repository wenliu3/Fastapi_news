from fastapi import FastAPI

app = FastAPI()
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/user/hello")
async def hello():
    return {"message": "我正在学习FastAPI......"}
