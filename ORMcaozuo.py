from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession
from fastapi import FastAPI,HTTPException
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
from datetime import datetime
from sqlalchemy import DateTime, String, Float, func
from fastapi import Depends
from sqlalchemy import select
import random
from pydantic import BaseModel
## 1. 启动 MySQL 数据库服务（在终端执行）
# docker start mysql-study
#创建Fastapi实例
app = FastAPI()
#1.创建异步引擎
ASYNC_DATABASE_URL="mysql+aiomysql://root:123456@localhost:3306/FastAPI_first?charset=utf8"
async_engine=create_async_engine(
  ASYNC_DATABASE_URL,
  echo=True,#可选，输出SQL日志
  pool_size=10,#设置连接池活跃的连接数
  max_overflow=20#允许的额外连接数
)
#2.定义模型类：基类＋表对应的模型类
#基类：创建时间，更新时间；书籍表：id，书名，作者，价格，出版社
class Base(DeclarativeBase):
  create_time:Mapped[datetime]=mapped_column(DateTime,insert_default=func.now(),comment="创建时间")
  update_time:Mapped[datetime]=mapped_column(DateTime,insert_default=func.now(),onupdate=func.now(),comment="修改时间")
class Book(Base):
  __tablename__="book"
  id:Mapped[int]=mapped_column(primary_key=True,comment="书籍id")
  bookname:Mapped[str]=mapped_column(String(255),comment="书名")
  author:Mapped[str]=mapped_column(String(255),comment="作者")
  price:Mapped[float]=mapped_column(Float,comment="价格")
  publisher:Mapped[str]=mapped_column(String(255),comment="出版社")
#用户表：用户id，用户名，密码，创建时间，更新时间
class User(Base):
  __tablename__="user"
  id:Mapped[int]=mapped_column(primary_key=True,comment="用户id")
  username:Mapped[str]=mapped_column(String(255),comment="用户名")
  password:Mapped[str]=mapped_column(String(255),comment="密码")
#3.建表：定义函数建表，Fastapi启动时候调用建表的函数
async def create_tables():
  #获取异步引擎，创建事务－建表
  async with async_engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)#使用模型类元数据来创建

@app.on_event("startup")
async def startup_event():
  await create_tables()
@app.get("/")
async def root():
    return {"message": "Hello World"}



#需求：查询功能的接口，查询图书。依赖注入：创建依赖项获取数据库绘画+depends注入路由处理函数
AsyncSessionLocal=async_sessionmaker(
  bind=async_engine,#绑定数据库引擎
  class_=AsyncSession,#指定对话类
  expire_on_commit=False,#提交后会话不过期，不会重新查询数据库
)
#依赖项
# 数据库依赖项
async def get_database():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
@app.get("/book/books")
async def get_book_list(db:AsyncSession=Depends(get_database)):
  #查询
  result=await db.execute(select(Book))
  #book=result.scalars().all()#获取所有
  #book=result.scalars().first()#获取第一条
  book = await db.get(Book,1)#获取id为1的数据
  
  return book

#需求：路径参数 书籍id
@app.get("/book/get_book/{book_id}")
async def get_book(book_id:int,db:AsyncSession=Depends(get_database)):
  result=await db.execute(select(Book).where(Book.id==book_id))
  book=result.scalar_one_or_none()
  return book
#需求：条件大于等于200
@app.get("/book/bookprice")
async def get_book_price(db:AsyncSession=Depends(get_database)):
  result=await db.execute(select(Book).where(Book.price>=200))
  books=result.scalars().all()
  return books
#模糊查询：
@app.get("/book/search_book")
async def get_search_book(db:AsyncSession=Depends(get_database)):
 
  #result=await db.execute(select(Book).where(Book.author.like("曹_")))
  #result=await db.execute(select(Book).where((Book.author.like("曹_"))|(Book.price>=200)))

  #需求：书籍id列表，数据库里的id如果在书籍id列表里面 就返回
  id_list=[1,2,4]
  result=await db.execute(select(Book).where(Book.id.in_(id_list)))

  books=result.scalars().all()
  return books
#聚合查询
@app.get("/book/count")
async def get_count(db:AsyncSession=Depends(get_database)):
  #result=await db.execute(select(func.count(Book.id)))
  #result=await db.execute(select(func.max(Book.price)))
  #result=await db.execute(select(func.sum(Book.price)))
  result=await db.execute(select(func.avg(Book.price)))
  num=result.scalar()#用来提取一个数值
  return num
#分页查询
@app.get("/book/getbooklist2")
async def get_books_list(
  page:int=1,
  page_size:int=3,
  db:AsyncSession=Depends(get_database)
  ):
  #（页码-1）*每页数量
  skip=(page-1)*page_size
  #offset 跳过的记录数；limit 每页的记录数
  stmt=select(Book).offset(skip).limit(page_size)
  result=await db.execute(stmt)
  books=result.scalars().all()
  return books

#新增数据
#需求：用户输入图书信息（id，书名，作者，价格，出版社）->新增
#用户输入->参数-> 请求体参数
class BookBase(BaseModel):
  id:int
  bookname:str
  author:str
  price:float
  publisher:str

@app.post("/book/add_book")

async def add_book(book:BookBase,db:AsyncSession=Depends(get_database)):
  #ORM对象->add->commit
  book_obj=Book(**book.__dict__)
  db.add(book_obj)
  await db.commit()
  return book
#更新数据
#先找，找到就修改然后commit，没找到就抛出异常
#需求：修改图书信息，先查再改
#思路：路径参数书籍id，作用是查找：请求体参数：作用是新数据（书名，作者，价格，出版社）
class BookUpdate(BaseModel):
  bookname:str
  author:str
  price:float
  publisher:str

@app.put("/book/update_book/(book_id)")
async def update_book(book_id:int,data:BookUpdate,db:AsyncSession=Depends(get_database)):
  #1.查找图书
  db_book= await db.get(Book,book_id)
  if db_book is None:
    raise HTTPException(
      status_code=404,
      detail="查无此书"
    )
  #重新赋值
  db_book.bookname=data.bookname
  db_book.author=data.author
  db_book.price=data.price
  db_book.publisher=data.publisher

  await db.commit()
  return db_book

#删除数据
#先查询，在删除，最后提交到数据库
@app.delete("/book/delete_book/{book_id}")
async def delete_book(book_id:int,db:AsyncSession=Depends(get_database)):
  #先查再删，最后提交
  db_book=await db.get(Book,book_id)
  if db_book is None:
    raise HTTPException(
      status_code=404,
      detail="查无此书"
    )
  #删除
  await db.delete(db_book)
  await db.commit()
  return {"msg":"删除图书成功"}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("ORMcaozuo:app", host="0.0.0.0", port=8000, reload=True)