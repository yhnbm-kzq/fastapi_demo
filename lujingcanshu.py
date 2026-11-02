from fastapi import FastAPI,Path
#创建Fastapi实例
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}
@app.get("/userid/{id}")
async def get_id(id:str):
  return {"id":id,"name":f"普通用户{id}"}
@app.get("/book/{id}")
async def get_book(id:int):
  return{"id":id,"title":f"这是第{id}本书"}
@app.get("/name/{name}")
async def get_name(name:str=Path(...,min_length=2,max_length=10)):
  return {"msg":f"这是{name}的信息"}

@app.get("/news/{id}")
async def get_newsid(id:int=Path(...,ge=1,le=100,description="新闻id")):
  return {"msg":f"这是第{id}条新闻"}
@app.get("/newsname/{newsname}")
async def get_newsname(newsname:str=Path(...,min_length=2,max_length=100,description="这是新闻名称")):
  return {"msg":f"新闻名称:{newsname}"}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("lujingcanshu:app", host="0.0.0.0", port=8000, reload=True)