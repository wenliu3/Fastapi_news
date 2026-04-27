from fastapi import FastAPI, HTTPException

app = FastAPI()
@app.get("/news/{id}")
async def get_new(id: int):
    id_list = {1, 2, 3, 4, 5, 6}
    if id not in id_list:
        raise HTTPException(status_code=404, detail="新闻不存在")
    return {"id": id }