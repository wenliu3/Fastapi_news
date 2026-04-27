from fastapi import FastAPI, Path

app = FastAPI()
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/book/{id}")
async def get_book(id: int):
    return {"id":  id, "message": "我正在学习FastAPI......"}

#路径参数path，类型注解
@app.get("/new/{id}")
async def get_new(id: int = Path(..., ge=1, le=100)):
    return {"id":  id, "message": "我正在学习FastAPI......"}

@app.get("/new/{name}")
async def get_new(name: str = Path(..., min_length=2, max_length=10)):
    return {"name":  name, "message": "我正在学习FastAPI......"}
