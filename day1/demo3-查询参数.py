from fastapi import FastAPI, Query

app = FastAPI()


# 查询参数: 用于资源过滤，排序 还有分页
@app.get("/name/name_list")
async def name_list(skip: int, limit: int = 10):
    return {"skip": skip, "limit": limit}


@app.get("/book/book_list")
async def get_book_list(price: float = Query(50,ge=50, le=100, description="价格范围50-100之间"),
                        sort: str = Query("Python开发", min_length=5, max_length=255, description="图书分类，长度限制 5~255")):
    return {"price": price, "sort": sort}