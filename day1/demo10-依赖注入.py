from fastapi import FastAPI, Query, Depends

app = FastAPI()

async def common_func(limit: int = Query(10, le=60), skip: int = Query(0, ge=0)):
    return {"limit": limit, "skip": skip}

@app.get("/news/new_list")
async def get_new_list(common = Depends(common_func)):
    return common