from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, String, Float, func, select
from datetime import datetime

# 1. 初始化 FastAPI 应用
app = FastAPI()

# 2. 创建异步数据库引擎
# 注意：把 123456 换成你自己的 MySQL root 密码
ASYNC_DATABASE_URL = "mysql+aiomysql://root:123456@localhost:3306/fastapi_first?charset=utf8"
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,
    pool_size=10,
    max_overflow=20,
)

# 3. 定义基类（包含创建时间、更新时间）
class Base(DeclarativeBase):
    create_time: Mapped[datetime] = mapped_column(
        DateTime, insert_default=func.now(), comment="创建时间"
    )
    update_time: Mapped[datetime] = mapped_column(
        DateTime, insert_default=func.now(), onupdate=func.now(), comment="更新时间"
    )

# 4. 定义书籍表模型
class Book(Base):
    __tablename__ = "book"

    id: Mapped[int] = mapped_column(primary_key=True, comment="书籍id")
    bookname: Mapped[str] = mapped_column(String(255), comment="书名")
    author: Mapped[str] = mapped_column(String(255), comment="作者")
    price: Mapped[float] = mapped_column(Float, comment="价格")
    publisher: Mapped[str] = mapped_column(String(255), comment="出版社")


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, comment="用户id")
    username: Mapped[str] = mapped_column(String(255), comment="用户名")
    password: Mapped[str] = mapped_column(String(255), comment="密码")

# 5. 启动时自动创建表
async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def startup_event():
    await create_tables()

# 6. 示例路由
@app.get("/")
async def root():
    return {"message": "Hello World"}



# 需求：查询功能的接口，查询图书 -> 依赖注入：创建依赖项获取数据会话 + Depends 注入路由处理函数
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine, # 绑定数据库引擎
    class_=AsyncSession, # 指定会话类
    expire_on_commit=False, # 提交后会话不过期，不会重新查询数据
)

# 创建依赖项
# 调用函数 → 创建 session → yield → 路由使用 → 恢复 → commit → close
async def get_database():
    async with AsyncSessionLocal() as session:
        try:
            yield session # 返回会话数据给路由处理函数
            await session.commit()
            print("成功commit")
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

@app.get("/book/books")
async def get_books(db: AsyncSession = Depends(get_database)):
    # 查询所有图书
    print("开始查询")
    result = await db.execute(select(Book)) # 返回ORM对象
    print("查询成功")
    # 获取所有数据
    # book = result.scalars().all()

    # 获取第一条 数据
    # book = result.scalars().first()

    # 用get
    book = await db.get(Book, 1) # 获取主键是1的单条数据
    return  book


# 条件查询
@app.get("/book/get_book/{book_id}")
async def get_book(book_id: int, db: AsyncSession = Depends(get_database)):
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none() # 获取单条数据或者 None
    return book


@app.get("/book/search_book")
async def search_book(db: AsyncSession = Depends(get_database)):
    # 模糊查询: 用like()，其中_表示任意一个字符，%表示任意多个字符
    # result = await db.execute(select(Book).where(Book.author.like("曹_")))
    # 与非查询：& | ~
    # result = await db.execute(select(Book).where((Book.author.like("曹%")) & (Book.price >=100)))
    # in查询
    id_list = [2, 4, 6]
    result = await db.execute(select(Book).where(Book.id.in_(id_list)))
    book = result.scalars().all()
    return book


# 聚合查询
@app.get("/book/aggregate_book")
async def aggregate_book(db: AsyncSession = Depends(get_database)):
    # result = await db.execute(select(func.count(Book.id)))
    # result = await db.execute(select(func.sum(Book.price)))
    # result = await db.execute(select(func.avg(Book.price)))
    result = await db.execute(select(func.max(Book.price)))
    num = result.scalar()
    return num

# 分页查询 offset: 跳过几条数据, limit: 取几条数据
@app.get("/book/page_book")
async def page_book(page: int = 1, limit: int=3, db: AsyncSession = Depends(get_database)):
    skip = (page - 1) * limit
    result = await db.execute(select(Book).offset(skip).limit(limit))
    book = result.scalars().all()
    return book

class BookBase(BaseModel):
    id: int
    bookname: str
    author: str
    price: float
    publisher: str

# 新增数据
@app.post("/book/add_book")
async def add_book(book: BookBase, db: AsyncSession = Depends(get_database)):
    # ORM对象 -> add -> commit
    book_obj = Book(**book.__dict__)
    db.add(book_obj)
    await db.commit()
    return book_obj


class BookUpdate(BaseModel):
    bookname: str
    author: str
    price: float
    publisher: str


# 修改数据
@app.put("/book/update_book/{book_id}")
async def update_book(book_id: int, data: BookUpdate, db: AsyncSession = Depends(get_database)):
    book = await db.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    book.bookname = data.bookname
    book.author = data.author
    book.price = data.price
    book.publisher = data.publisher
    await db.commit()
    return book

# 删除数据
@app.delete("/book/delete_book/{book_id}")
async def delete_book(book_id: int, db: AsyncSession = Depends(get_database)):
    book = await db.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book of found")
    await db.delete(book)
    await db.commit()
    return {"message": "删除成功"}



















