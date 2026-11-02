from fastapi import FastAPI,Path,Query,HTTPException
from pydantic import BaseModel,Field
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse

#创建Fastapi实例
app = FastAPI()

@app.middleware("http")
async def middleware1(request,call_next):
  print("中间件1start")
  response=await call_next(request)
  print("中间件1end")
  return response
@app.middleware("http")
async def middleware2(request,call_next):
  print("中间件2start")
  response=await call_next(request)
  print("中间件2end")
  return response
@app.get("/")
async def root():
    return {"message": "Hello World"}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("zhongjianjian:app", host="0.0.0.0", port=8000, reload=True)