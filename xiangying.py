from fastapi import FastAPI,Path,Query
from pydantic import BaseModel,Field
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
#创建Fastapi实例
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}
#接口，响应html代码
@app.get("/html/",response_class=HTMLResponse)
async def get_html():
  return "<h1>这是一级标题</h1>"
#接口，返回一张图片
@app.get("/files/")
async def get_files():
  path="/workspace/example/fastapi_demo/1.jpg"
  return FileResponse(path)
#需求：新闻接口，响应数据格式 id，title，content
class News(BaseModel):
  id:int
  title:str
  content:str
@app.get("/news/{id}",response_model=News)
async def get_news(id:int):
  return {
    "id":id,
    "title":f"这是第{id}本书",
    "content":"这是一本好书"
  }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("xiangying:app", host="0.0.0.0", port=8000, reload=True)