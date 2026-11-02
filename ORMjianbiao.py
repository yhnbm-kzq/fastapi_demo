from sqlalchemy.ext.asyncio import create_async_engine
from fastapi import FastAPI
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
from datetime import datetime
from sqlalchemy import DateTime, String, Float, func
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






if __name__ == "__main__":
    import uvicorn
    uvicorn.run("ORMjianbiao:app", host="0.0.0.0", port=8000, reload=True)