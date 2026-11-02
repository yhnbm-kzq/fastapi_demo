from fastapi import FastAPI,Path,Query,HTTPException
from pydantic import BaseModel,Field
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse

#创建Fastapi实例
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}
#需求：按id查询新闻，但id在1－6之间
@app.get("/news/{id}")
async def get_news(id:int):
  id_list=[1,2,3,4,5,6]
  if id not in id_list:
    raise HTTPException(status_code=404,detail="新闻不存在")

  return {"id":id}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("yichangxiangying:app", host="0.0.0.0", port=8000, reload=True)