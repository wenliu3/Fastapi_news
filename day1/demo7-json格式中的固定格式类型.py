from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
class New(BaseModel):
    id : int
    title: str
    dcr: str

@app.get("/new/{id}", response_model=New)
async def get_new(id: int):
    return {
        "id": id,
        "title": f"这是一个{id}的标题",
        "dcr": f"这是一个{id}的描述"
    }