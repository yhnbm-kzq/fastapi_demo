# FastAPI 学习笔记：第 1～29 集

本仓库用于记录黑马程序员 FastAPI 课程的练习代码。本 README 按前 29 集顺序整理「解决什么问题 → 如何使用 → 如何验证」，以图书管理为主要案例。

- [课程视频](https://www.bilibili.com/video/BV1zV2QBtE39/)
- [练习仓库](https://github.com/yhnbm-kzq/fastapi_demo)
- 学习范围：基础路由、参数校验、响应、异常、中间件、依赖注入，以及 SQLAlchemy 异步 ORM 增删改查。

> 整理依据：B 站公开分集目录、仓库代码（快照 `77e3fb3`）与官方文档；未逐帧观看视频或核对字幕。下文案例是为理解知识点编写的讲解示例，不是视频逐字稿，也不表示仓库已包含所有改进。示例使用 Python 3.10+、Pydantic 2、SQLAlchemy 2 风格。

## 目录与代码对照

| 集数 | 分集主题 | 仓库练习 |
| --- | --- | --- |
| 01 | 从入门到实战导学 | 本文学习路线 |
| 02 | FastAPI 框架简介 | 框架整体认识 |
| 03 | 第一个 FastAPI 程序 | 各文件中的 `app = FastAPI()` |
| 04 | 路由 | [luyou.py](luyou.py) |
| 05 | 参数简介和路径参数 | [lujingcanshu.py](lujingcanshu.py) |
| 06 | 路径参数：Path 类型注解 | [lujingcanshu.py](lujingcanshu.py) |
| 07 | 查询参数和 Query 类型注解 | [chaxuncanshu.py](chaxuncanshu.py) |
| 08 | 请求体参数 | [qingqiuticanshu.py](qingqiuticanshu.py) |
| 09 | 请求体参数：Field 类型注解 | 同上 |
| 10 | JSON 格式响应 | 各路由返回字典的案例 |
| 11 | HTML 格式响应 | [xiangying.py](xiangying.py) |
| 12 | 文件格式响应 | 同上 |
| 13 | 自定义响应数据格式 | 同上，`response_model` |
| 14 | 异常响应处理 | [yichangxiangying.py](yichangxiangying.py) |
| 15 | 中间件 | [zhongjianjian.py](zhongjianjian.py) |
| 16 | 依赖注入 | [yilaizhuru.py](yilaizhuru.py) |
| 17 | ORM 简介及安装 | [ORMjianbiao.py](ORMjianbiao.py) |
| 18 | ORM 建表 | 同上 |
| 19 | 在路由中使用 ORM | [ORMcaozuo.py](ORMcaozuo.py) |
| 20 | 查询数据 | 同上 |
| 21 | 条件查询：比较判断 | 同上 |
| 22 | 条件查询：模糊、与非、包含 | 同上 |
| 23 | 聚合查询 | 同上 |
| 24 | 分页查询 | 同上 |
| 25 | 查询总结 | 同上 |
| 26 | 新增数据 | 同上 |
| 27 | 更新数据 | 同上 |
| 28 | 删除数据 | 同上 |
| 29 | ORM 总结 | 本文 CRUD 串联练习 |

## 先运行练习

仓库中多个 `.py` 文件各自创建一个应用，学习时一次启动一个。以下命令在仓库根目录执行。

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
# 当前 requirements.txt 只有 fastapi 和 uvicorn，ORM 练习还需安装：
.\.venv\Scripts\python.exe -m pip install "sqlalchemy>=2,<3" aiomysql
.\.venv\Scripts\python.exe -m uvicorn luyou:app --reload
```

`luyou:app` 表示导入 `luyou.py` 内的 `app` 对象；切换练习时将模块名替换为 `lujingcanshu`、`ORMcaozuo` 等。`--reload` 用于本地开发。

- 首页：`http://127.0.0.1:8000/`
- Swagger 接口调试：`http://127.0.0.1:8000/docs`
- ReDoc 文档：`http://127.0.0.1:8000/redoc`
- OpenAPI 描述：`http://127.0.0.1:8000/openapi.json`

运行 ORM 文件前，先启动 MySQL，创建 `FastAPI_first` 数据库，再按自己的环境修改连接地址。代码中的 `create_all()` 创建表，不负责创建数据库。若本机确实已有名为 `mysql-study` 的容器，可以执行 `docker start mysql-study`；它不是通用的数据库安装命令。

## 01｜导学：理解接口开发的完整链路

**功能：**知道每个知识点处于请求处理的哪一步，避免只记 API 名称。

以「按价格查询图书」为例：

```text
客户端 GET /books?min_price=50
  → 中间件：记录耗时等通用处理
  → 路由匹配、参数校验、依赖解析
  → 处理函数：使用数据库会话查询图书
  → 响应模型组织输出
  → 中间件处理响应 → 客户端收到 JSON
```

学完前 29 集，应能完成图书的查询、新增、更新、删除，并解释错误参数、图书不存在和数据库提交分别在哪一层处理。

## 02｜FastAPI 框架简介

**功能：**将 Python 函数变成 HTTP 接口，并利用类型注解完成参数解析、校验和文档生成。

| 组件 | 在项目中的作用 | 类比 |
| --- | --- | --- |
| FastAPI | 定义路由、参数、依赖和响应 | 接待与业务调度 |
| Uvicorn | ASGI 服务器，接收 HTTP 请求并运行应用 | 服务入口 |
| Pydantic | 校验、转换、序列化数据 | 数据检查员 |
| SQLAlchemy | 用 Python 表达数据库查询与持久化 | 数据访问工具 |
| aiomysql | 异步连接 MySQL 的驱动 | 与数据库通信的通道 |

例如声明 `book_id: int` 后，路径中的 `"12"` 通常能转换为整数 `12`，`"abc"` 则会校验失败。这体现了「类型声明参与运行时校验」，不是只有编辑器提示。

## 03｜第一个 FastAPI 程序

**功能：**建立最小可访问的服务。

将下面代码单独保存为 `main.py`：

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

执行 `python -m uvicorn main:app --reload`，访问 `/`，预期得到 `{"message":"Hello World"}`。

`async def` 允许函数使用 `await` 等待异步 I/O，但不会自动让所有代码变成非阻塞代码。后面的异步数据库操作使用 `await db.execute(...)`；不要在异步路由里直接放长时间的同步阻塞调用。

## 04｜路由

**功能：**把「请求方法 + URL 路径」映射到处理函数。

```python
@app.get("/hello")
async def hello():
    return {"msg": "你好 FastAPI"}
```

访问 `GET /hello` 才会调用 `hello()`。常见图书接口约定：

| 方法 | 路径 | 作用 |
| --- | --- | --- |
| GET | `/books` | 查询列表 |
| GET | `/books/{book_id}` | 查询一本书 |
| POST | `/books` | 新增 |
| PUT | `/books/{book_id}` | 整体更新业务字段 |
| DELETE | `/books/{book_id}` | 删除 |

同一路径可以有不同方法。浏览器地址栏通常发送 GET，调试 POST/PUT/DELETE 可用 `/docs`。若有 `/books/search` 和 `/books/{book_id}`，应先声明固定路径，防止 `search` 被动态路径接走。

## 05｜参数简介和路径参数

**功能：**从 URL 中识别要操作的具体资源。

```python
@app.get("/books/{book_id}")
async def get_book(book_id: int):
    return {"id": book_id, "title": f"第 {book_id} 本书"}
```

- `/books/3` → `book_id` 为整数 `3`。
- `/books/abc` → 默认返回 HTTP 422，处理函数不会正常执行。
- 路由必须用 `{book_id}`，并与函数参数名一致。

三类参数的直观区别：`/books/3` 中的 `3` 是路径参数；`/books?author=张三` 中的 `author` 是查询参数；新增书籍时提交的 JSON 是请求体。

## 06｜Path：约束路径参数

**功能：**不仅检查类型，还检查编号、长度等业务范围。

```python
from fastapi import Path

@app.get("/news/{news_id}")
async def get_news(news_id: int = Path(..., ge=1, le=100, description="新闻编号")):
    return {"id": news_id}
```

`...` 表示必填；`ge` 为大于等于，`le` 为小于等于。`/news/1` 合法，`/news/0` 和 `/news/101` 返回 422。字符串可使用 `min_length`、`max_length`。

**理解边界：**编号符合范围，不代表数据库一定存在这条记录；不存在仍应在业务查询后返回 404。

## 07｜查询参数与 Query

**功能：**表达筛选、搜索、分页等附加条件。

```python
from fastapi import Query

@app.get("/books")
async def list_books(
    keyword: str | None = Query(None, min_length=2),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    return {"keyword": keyword, "page": page, "page_size": page_size}
```

`GET /books?keyword=Python&page=2&page_size=5` 返回对应参数；不传时使用默认值；`page=0` 返回 422。需要必填的查询参数可写 `price: float = Query(..., gt=0)`。

`str | None` 表示允许空值；是否允许省略还要看默认值。写成 `= None` 才表示可省略并默认取空值。

## 08｜请求体参数

**功能：**一次接收多个有结构的字段，适合新增或修改数据。

```python
from pydantic import BaseModel

class BookCreate(BaseModel):
    bookname: str
    author: str
    price: float
    publisher: str

@app.post("/books")
async def create_book(data: BookCreate):
    return data
```

在 `/docs` 的请求体输入：

```json
{"bookname":"Python入门","author":"张三","price":59.9,"publisher":"学习出版社"}
```

FastAPI 会把 JSON 解析成 `BookCreate`，函数里可用 `data.bookname`。缺少必填字段会返回 422。这里仅回显数据，**尚未保存数据库**。

## 09｜Field：约束请求体字段

**功能：**把数据规则写在 Pydantic 模型上，让错误在进入业务逻辑前被发现。

```python
from pydantic import BaseModel, Field

class BookCreate(BaseModel):
    bookname: str = Field(..., min_length=2, max_length=255)
    author: str = Field(..., min_length=2, max_length=255)
    price: float = Field(..., gt=0, description="价格，必须大于零")
    publisher: str = Field("学习出版社", max_length=255)
```

价格为 `-1`、书名只有一个字符都会返回 422；省略 `publisher` 则使用默认出版社。

| 声明 | 作用位置 |
| --- | --- |
| `Path` | 路径参数 |
| `Query` | 查询参数 |
| `Field` | Pydantic 模型字段 |

仓库的 `price: str = Field(..., gt='0')` 应改为数值类型和数值界限，例如 `price: float = Field(..., gt=0)`。真实金额系统还需要考虑十进制定点精度，可进一步学习 `Decimal` 与数据库 `Numeric`。

## 10｜JSON 格式响应

**功能：**向前端返回结构化数据。

```python
@app.get("/book-summary")
async def summary():
    return {"total": 1, "items": [{"id": 1, "bookname": "Python入门"}]}
```

一般直接返回字典、列表或 Pydantic 模型即可，由框架生成 JSON 响应。通常不需要先 `json.dumps()`，否则可能得到被再次编码的字符串。HTTP 状态码和 JSON 中的业务字段是两件事：返回 `{"code":404}` 并不会自动把 HTTP 状态改成 404。

## 11｜HTML 格式响应

**功能：**让浏览器将响应作为 HTML 页面渲染。

```python
from fastapi.responses import HTMLResponse

@app.get("/html", response_class=HTMLResponse)
async def html_page():
    return "<h1>我的图书管理系统</h1><p>欢迎学习 FastAPI</p>"
```

访问 `/html` 会看到标题和段落。`response_class` 控制响应的表现形式；HTML 内容包含用户输入时应正确转义，避免直接拼接不可信内容。

## 12｜文件格式响应

**功能：**返回图片、PDF 或下载文件的内容。

```python
from pathlib import Path
from fastapi.responses import FileResponse

@app.get("/cover")
async def cover():
    image = Path(__file__).resolve().parent / "1.jpg"
    return FileResponse(image, media_type="image/jpeg")
```

`FileResponse` 发送文件内容；直接返回文件路径字符串只会发送字符串。增加 `filename="cover.jpg"` 可指定下载文件名。此处使用源码文件所在目录定位图片，避免工作目录变化造成找不到文件；仓库 `xiangying.py` 中的固定 `/workspace/.../1.jpg` 路径需要相应调整。

## 13｜自定义响应数据格式

**功能：**通过响应模型明确输出字段、生成文档，并过滤不应返回的字段。

```python
class UserOut(BaseModel):
    id: int
    username: str

@app.get("/profile", response_model=UserOut)
async def profile():
    return {"id": 1, "username": "learner", "password": "仅作演示"}
```

响应只有 `id`、`username`，不会包含 `password`。仓库的 `News` 模型用于约定 `id/title/content`，作用相同。

输入模型约束「客户端应提交什么」，输出模型约束「服务端应返回什么」。输出不符合响应模型通常属于服务端错误，不是客户端的 422。直接返回 `Response`/`JSONResponse` 对象时，不会再自动应用普通 `response_model` 处理流程。

## 14｜异常响应处理

**功能：**终止当前业务处理，并返回明确的错误状态。

```python
from fastapi import HTTPException

@app.get("/news/{news_id}")
async def news(news_id: int):
    if news_id not in [1, 2, 3, 4, 5, 6]:
        raise HTTPException(status_code=404, detail="新闻不存在")
    return {"id": news_id}
```

`/news/99` → HTTP 404，正文 `{"detail":"新闻不存在"}`。注意使用 `raise` 抛出异常。

| 状态码 | 在练习中的含义 |
| --- | --- |
| 200 | 查询或更新成功 |
| 201 | 新增成功，可在 POST 装饰器中声明 |
| 404 | 路径不存在或指定资源不存在 |
| 405 | 路径存在，但请求方法不支持 |
| 422 | 请求参数未通过校验 |
| 500 | 未处理的服务端错误 |

## 15｜中间件

**功能：**在多个接口外层统一执行请求前、响应后的逻辑，例如记录耗时。

```python
import time

@app.middleware("http")
async def timing(request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time"] = f"{time.perf_counter() - start:.6f}"
    return response
```

`call_next(request)` 将请求交给内部处理链，返回后可修改响应头。在 `/docs` 或浏览器开发者工具中查看 `X-Process-Time`。

仓库先注册中间件 1、再注册中间件 2，普通成功请求打印顺序为：`2 start → 1 start → 路由 → 1 end → 2 end`。后注册的在更外层。

## 16｜依赖注入

**功能：**复用参数解析、资源获取等逻辑，由框架执行依赖并把结果传给接口。

```python
from fastapi import Depends, Query

async def pagination(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=60),
):
    return {"skip": skip, "limit": limit}

@app.get("/users")
async def users(params: dict = Depends(pagination)):
    return params

@app.get("/news")
async def news_list(params: dict = Depends(pagination)):
    return params
```

两个接口共用参数规则，修改规则只需改依赖函数。写 `Depends(pagination)`，不要写 `Depends(pagination())`。中间件适合全局请求处理，依赖适合给指定接口提供参数、身份或数据库会话。使用 `yield` 的依赖还能管理资源清理，下一节 ORM 会使用它。

## 17｜ORM 简介及安装

**功能：**将 Python 类、对象、属性分别对应数据库的表、行、列。

```text
Book 类     ↔ book 表
Book 对象   ↔ 一条图书记录
book.price  ↔ price 列的值
```

本仓库使用 SQLAlchemy 异步 API 和 MySQL 驱动 aiomysql：

```powershell
python -m pip install "sqlalchemy>=2,<3" aiomysql
```

引擎配置示例：

```python
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    "mysql+aiomysql://用户名:密码@localhost:3306/FastAPI_first?charset=utf8mb4",
    echo=True,
    pool_size=10,
    max_overflow=20,
)
```

`echo=True` 便于观察生成的 SQL；`pool_size` 设置连接池容量，`max_overflow` 允许繁忙时临时增加连接。实际账号、密码与数据库名称要自行配置，正式项目可从环境变量读取连接串。

## 18｜ORM 建表

**功能：**用模型声明表结构，再创建数据库中不存在的表。

以下定义供第 19～28 节 ORM 片段共用：

```python
from sqlalchemy import String, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Book(Base):
    __tablename__ = "book"
    id: Mapped[int] = mapped_column(primary_key=True)
    bookname: Mapped[str] = mapped_column(String(255))
    author: Mapped[str] = mapped_column(String(255))
    price: Mapped[float] = mapped_column(Float)
    publisher: Mapped[str] = mapped_column(String(255))

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

`__tablename__` 是表名，`Mapped[...]` 声明映射属性，`mapped_column()` 配置列。`run_sync()` 让 SQLAlchemy 的同步建表 API 在异步连接中执行。

仓库还在基类中定义了创建时间和更新时间，供多张表复用。`create_all()` 不会自动把已有表迁移成新结构；后续修改列结构需要数据库迁移工具。

仓库使用 `@app.on_event("startup")` 调用建表；新示例可使用官方推荐的 lifespan（放在模型和引擎定义之后）：

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    try:
        yield
    finally:
        await engine.dispose()

app = FastAPI(lifespan=lifespan)
```

## 19｜在路由中使用 ORM

**功能：**为请求提供数据库会话，并在使用后关闭资源。

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise

@app.get("/books/{book_id}")
async def get_book(book_id: int, db: AsyncSession = Depends(get_db)):
    book = await db.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="图书不存在")
    return book
```

引擎管理连接池，会话管理当前数据库操作与事务；二者不是同一个对象。`yield` 把会话交给接口，退出上下文时关闭会话。此依赖不会自动提交，写操作在路由中显式 `commit()`。

`expire_on_commit=False` 防止提交后自动将已加载属性标记为过期，但不会自动加载所有延迟属性。并发任务不应共用同一个 `AsyncSession`。

## 20｜查询数据

**功能：**读取全部图书、第一本书或指定主键的书。

```python
from sqlalchemy import select

# 以下片段均在 async 路由/函数中，db 来自 get_db 依赖
result = await db.execute(select(Book))
books = result.scalars().all()

result = await db.execute(select(Book).order_by(Book.id).limit(1))
first_book = result.scalars().first()

book = await db.get(Book, 1)
```

`execute()` 得到结果对象，`scalars()` 提取每行第一列；`select(Book)` 的第一列就是 Book 实体。`all()` 得列表，没有记录时为 `[]`；`first()` 没有记录时为 `None`。在这种缓冲结果用法中，`execute()` 要 `await`，结果的 `scalars().all()` 不需要。

仓库 `/book/books` 虽然先执行了列表查询，但实际返回的是 `await db.get(Book, 1)` 的结果；要返回列表，应返回 `result.scalars().all()`。

## 21｜条件查询：比较判断

**功能：**把筛选条件交给数据库执行，避免读出全部数据后再用 Python 过滤。

```python
stmt = select(Book).where(Book.price >= 200)
books = (await db.execute(stmt)).scalars().all()

stmt = select(Book).where(Book.id == book_id)
book = (await db.execute(stmt)).scalar_one_or_none()
```

常用比较：`==`、`!=`、`>`、`>=`、`<`、`<=`。判断 SQL 空值可用 `Book.author.is_(None)`，但本例作者列本身不允许空值。

`Book.price >= 200` 构造 SQL 条件，并不是立即比较某个 Python 对象。主键条件最多匹配一行，适合 `scalar_one_or_none()`；普通作者条件可能匹配多行，应使用列表提取方式。

## 22｜条件查询：模糊、与或非、包含

**功能：**组合搜索条件。

```python
from sqlalchemy import and_, or_, not_

# % 匹配任意长度，_ 匹配一个字符
stmt = select(Book).where(Book.bookname.like("%Python%"))
stmt = select(Book).where(Book.author.like("曹_"))

# 与：作者张三，且价格至少 50
stmt = select(Book).where(and_(Book.author == "张三", Book.price >= 50))
# 多个 where 参数也表示与
stmt = select(Book).where(Book.author == "张三", Book.price >= 50)

# 或：张三的书，或者价格至少 200
stmt = select(Book).where(or_(Book.author == "张三", Book.price >= 200))
# 非：排除张三的书
stmt = select(Book).where(not_(Book.author == "张三"))
# 包含：只查指定编号
stmt = select(Book).where(Book.id.in_([1, 2, 4]))

books = (await db.execute(stmt)).scalars().all()
```

以上每次赋值都是一个独立示例，最后执行的是最后一个 `stmt`。也可使用 `(条件1) & (条件2)`、`|`、`~`，但要加括号，不能用 Python 的 `and/or/not` 替代 SQL 表达式组合。

## 23｜聚合查询

**功能：**让数据库直接计算数量、最大值、总和与平均值。

```python
from sqlalchemy import func

total = (await db.execute(select(func.count(Book.id)))).scalar_one()
max_price = (await db.execute(select(func.max(Book.price)))).scalar_one()
sum_price = (await db.execute(select(func.sum(Book.price)))).scalar_one()
avg_price = (await db.execute(select(func.avg(Book.price)))).scalar_one()
```

假设只有两本书，价格为 50 和 100，则数量为 2、最高价 100、总价 150、均价 75。空表的 `count` 为 0，其余这些聚合通常返回 `None`。

聚合结果不是 Book 对象，因此使用 `scalar()`/`scalar_one()` 提取数值。仓库 `/book/count` 当前执行的是 `avg`，虽然路径叫 count，返回的实际是平均价格。

## 24｜分页查询

**功能：**每次只返回一部分数据，控制接口返回量。

```python
@app.get("/books")
async def list_books(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * page_size
    stmt = select(Book).order_by(Book.id).offset(offset).limit(page_size)
    items = (await db.execute(stmt)).scalars().all()
    total = (await db.execute(select(func.count(Book.id)))).scalar_one()
    return {"page": page, "page_size": page_size, "total": total, "items": items}
```

`page=2&page_size=3` → 跳过 3 条，再取最多 3 条。`offset()` 表示跳过多少行，`limit()` 表示最多取多少行。加上唯一且明确的排序（这里是主键），避免结果顺序不确定；有筛选条件时，总数查询也要应用相同条件。

## 25｜查询总结

**功能：**根据返回形状选择正确的结果提取方式。

| 查询意图 | 语句 | 提取方式 |
| --- | --- | --- |
| 多条实体 | `select(Book)` | `result.scalars().all()` |
| 第一条实体 | `select(Book).limit(1)` | `result.scalars().first()` |
| 至多一条实体 | `select(Book).where(Book.id == 1)` | `result.scalar_one_or_none()` |
| 根据主键查询 | `await db.get(Book, 1)` | 直接得到实体或 `None` |
| 单个统计值 | `select(func.count(Book.id))` | `result.scalar_one()` |
| 多列 | `select(Book.bookname, Book.price)` | `result.all()`，得到行列表 |

`scalar_one_or_none()` 如果实际返回多行会抛异常；`first()` 则取第一行，不验证唯一性。`select(Book.bookname, Book.price)` 若使用 `scalars()`，只会保留第一列书名，价格会丢失。

## 26｜新增数据

**功能：**将通过校验的输入模型转换成 ORM 对象并提交数据库。

复用第 09 节的 `BookCreate`，由数据库生成主键，无须客户端提交 id：

```python
@app.post("/books", status_code=201)
async def create_book(data: BookCreate, db: AsyncSession = Depends(get_db)):
    book = Book(**data.model_dump())
    db.add(book)
    await db.commit()
    await db.refresh(book)
    return book
```

操作链为 `请求体 → Pydantic 校验 → ORM 对象 → add → commit → refresh`。

- `model_dump()`：Pydantic 2 将输入模型转成字典，比读取 `__dict__` 更明确。
- `add()`：将对象加入会话，这一步不需要 `await`。
- `commit()`：刷新待写入数据并提交事务。
- `refresh()`：重新从数据库加载对象，取得生成的主键或默认值。

调用后记下返回的 `id`，再查询此 id，验证数据确实持久化。仓库原有 `BookBase` 仍要求提交 id，使用原接口时应遵循其实际模型。

## 27｜更新数据

**功能：**查到目标记录后，修改字段并提交。

```python
class BookUpdate(BookCreate):
    pass

@app.put("/books/{book_id}")
async def update_book(
    book_id: int, data: BookUpdate,
    db: AsyncSession = Depends(get_db),
):
    book = await db.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="图书不存在")
    for name, value in data.model_dump().items():
        setattr(book, name, value)
    await db.commit()
    await db.refresh(book)
    return book
```

这里输入模型约定完整业务字段；对会话已加载的对象修改属性后，提交时 ORM 会跟踪变化，无须再次 `add()`。若以后实现只修改部分字段的 PATCH，可单独定义可省略字段的模型，并用 `model_dump(exclude_unset=True)` 读取实际提交的字段。

**仓库待修正：**`/book/update_book/(book_id)` 使用了圆括号，是字面路径，`book_id` 会被当作查询参数。应改成 `/book/update_book/{book_id}` 才是路径参数。

## 28｜删除数据

**功能：**先确认资源存在，再删除并提交。

```python
@app.delete("/books/{book_id}")
async def delete_book(book_id: int, db: AsyncSession = Depends(get_db)):
    book = await db.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="图书不存在")
    await db.delete(book)
    await db.commit()
    return {"msg": "删除图书成功", "id": book_id}
```

`AsyncSession.delete()` 需要 `await`。删除后再次查询同一 id，应得到 404。本例返回 HTTP 200 和 JSON；若使用 204 No Content，则不应再返回 JSON 正文。

## 29｜ORM 总结：串联图书 CRUD

**功能：**把前面的参数、依赖、异常和 ORM 操作组合成完整业务。

```text
POST 新增 → 得到 id → GET 查询 → PUT 更新 → GET 验证新值
    → DELETE 删除 → GET 验证 404
```

| 动作 | 数据来源 | ORM 核心流程 |
| --- | --- | --- |
| 列表查询 | Query 筛选及分页 | select → execute → scalars().all() |
| 详情查询 | Path 主键 | get → 判断是否为 None |
| 新增 | 请求体模型 | 构造对象 → add → commit → refresh |
| 更新 | Path 主键 + 请求体 | get → 判断存在 → 改属性 → commit |
| 删除 | Path 主键 | get → 判断存在 → delete → commit |

必须分清两种模型：`BookCreate(BaseModel)` 负责接口数据校验；`Book(Base)` 负责数据库表映射。Pydantic 模型不会自动建表，ORM 对象也不能替代所有输入校验。

事务可以理解为「一组数据库修改的整体提交」：成功 `commit()`，异常 `rollback()`。例如一次新增两本书，若第二本违反约束导致提交失败，应回滚本次事务，避免留下不完整结果。

返回 ORM 数据时可进一步声明输出模型（应用于前述路由的 `response_model`）：

```python
from pydantic import ConfigDict

class BookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    bookname: str
    author: str
    price: float
    publisher: str

# 单本：@app.get("/books/{book_id}", response_model=BookOut)
# 列表：@app.get("/books", response_model=list[BookOut])
# 注意：第 24 节返回的是含 items/total 的分页字典，需另外定义分页输出模型。
```

`from_attributes=True` 允许 Pydantic 从 ORM 对象属性读取字段。只声明要输出的字段，有助于稳定接口结构。

## 实践验证清单

上面的分节代码是讲解片段，包含不同版本的同名路由；不要把所有片段无差别拼到同一个文件。基础片段需有 `app`，ORM 片段需共用引擎、模型、会话依赖及必要导入（`HTTPException`、`Query`、`select`、`func` 等）。以下按你仓库现有接口操作，先完成下节列出的必要修正。

1. 启动 `lujingcanshu:app`：访问 `/news/1` 应成功，`/news/0` 应为 422。
2. 启动 `chaxuncanshu:app`：访问 `/books/?price=60` 应成功，省略必填 `price` 应为 422。
3. 启动 `qingqiuticanshu:app`：向 `/book/` 提交合法图书 JSON，再将价格改成负数验证 422。此文件使用 `name` 字段，ORM 文件使用 `bookname`，要按实际接口填写。
4. 启动 `yichangxiangying:app`：访问 `/news/99` 应为 404。
5. 启动 `ORMcaozuo:app`，在 `/docs` 调用 `POST /book/add_book`，输入下面的 JSON（使用尚未存在的 id）：

```json
{"id":101,"bookname":"Python入门","author":"张三","price":59.9,"publisher":"学习出版社"}
```

6. 调用 `GET /book/get_book/101`，确认内容已写入。
7. 修正更新路由后，调用 `PUT /book/update_book/101`，提交不含 id 的完整图书信息，将价格改成 `69.9`，再次查询确认更新。
8. 调用 `DELETE /book/delete_book/101`，再次查询。仓库当前详情接口会对不存在的书返回 `null`；若加入第 19 节的存在性判断，则应为 404。

## 对照当前练习代码需要注意的地方

以下为阅读仓库快照发现的问题或改进点，本 README 没有直接修改源码：

| 位置 | 当前情况 | 建议 |
| --- | --- | --- |
| `requirements.txt` | 只有 fastapi、uvicorn | 补充 sqlalchemy、aiomysql，验证环境后记录依赖版本 |
| `qingqiuticanshu.py` | 价格为 `str`，`gt` 也是字符串 | 改为数值字段，例如 `float` 与 `gt=0` |
| `ORMcaozuo.py` 更新接口 | 路径使用 `(book_id)` | 改成 `{book_id}` |
| `xiangying.py` 文件响应 | 图片位置写死为其他环境的路径 | 使用 `Path(__file__).resolve().parent / "1.jpg"` |
| `/book/books` | 执行列表查询，却返回 id=1 的单本书 | 按实际目的返回列表或更名为详情接口 |
| `/book/count` | 实际查询平均价格 | 将路径改为平均价格含义，或改成 count 查询 |
| 分页接口 | 未限制页码、每页数量，也没有显式排序 | 使用 Query 校验，加 `order_by(Book.id)` |
| 新增接口 | 用 `book.__dict__` 构造 ORM 对象 | Pydantic 2 改用 `book.model_dump()` |
| 详情接口 | 查不到记录直接返回 `None` | 按接口约定抛出 HTTP 404 |
| ORM 配置 | 数据库账号密码写在代码里 | 改用环境变量管理真实连接信息 |
| 注册练习 | 直接返回包含密码的输入模型 | 输出模型排除密码；真实注册需散列存储密码 |

## 复习时回答这些问题

- `Path`、`Query`、`Field` 分别约束哪一层数据？
- 为什么 `/books/abc` 返回 422，而合法编号找不到图书应返回 404？
- 为什么普通字典可以直接返回，但文件要用 `FileResponse`？
- 中间件与 `Depends()` 各自适合复用什么逻辑？
- 为什么 `select(Book)` 用 `scalars()`，而查询书名和价格两列不能只用它？
- `add()` 与 `commit()` 有何不同？为什么提交失败要回滚？
- 为什么 `create_all()` 不能代替表结构迁移？

## 参考资料

分集顺序来自[课程页面](https://www.bilibili.com/video/BV1zV2QBtE39/)，代码对照来自[本仓库](https://github.com/yhnbm-kzq/fastapi_demo)。下列官方文档用于核对示例写法和进一步阅读：

- [FastAPI：路径参数与校验](https://fastapi.tiangolo.com/tutorial/path-params-numeric-validations/)
- [FastAPI：查询参数与校验](https://fastapi.tiangolo.com/tutorial/query-params-str-validations/)
- [FastAPI：请求体](https://fastapi.tiangolo.com/tutorial/body/)
- [Pydantic：字段定义](https://docs.pydantic.dev/latest/concepts/fields/)
- [FastAPI：响应模型](https://fastapi.tiangolo.com/tutorial/response-model/)
- [FastAPI：自定义响应](https://fastapi.tiangolo.com/advanced/custom-response/)
- [FastAPI：错误处理](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [FastAPI：中间件](https://fastapi.tiangolo.com/tutorial/middleware/)
- [FastAPI：依赖注入](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [FastAPI：lifespan](https://fastapi.tiangolo.com/advanced/events/)
- [SQLAlchemy：异步 ORM](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [SQLAlchemy：ORM 查询指南](https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html)
