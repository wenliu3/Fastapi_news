from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()
class Book(BaseModel):
    name: str = Field(..., min_length=2, max_length=20, description="图书名称，长度限制 2~20")
    author: str = Field(..., min_length=2, max_length=10, description="作者名称，长度限制 2~10")
    public: str = Field("黑马出版社")
    price: float = Field(..., gt=0, description="图书价格，必须大于0")
#创建、更新、携带大量数据，如：json
#需求:设计接口新增图书，图书信息包含:书名、作者、出版社、售价
@app.post("/book")
async def create_book(book: Book):
    return book