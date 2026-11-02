from fastapi import FastAPI,Path,Query,HTTPException,Depends#导入依赖项
from pydantic import BaseModel,Field
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse

#创建Fastapi实例
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}
#分页参数逻辑共用，用户列表和新闻列表
#1.依赖项
async def common_parameters(
  skip:int=Query(0,ge=0),
  limit:int=Query(10,le=60)
):
  return {"skip":skip,"limit":limit}
#3.声明依赖项
@app.get("/user/userlist/")
async def get_userlist(commons=Depends(common_parameters)):
  return commons

@app.get("/news/newslist/")
async def get_newslist(commons=Depends(common_parameters)):
  return commons

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("yilaizhuru:app", host="0.0.0.0", port=8000, reload=True)