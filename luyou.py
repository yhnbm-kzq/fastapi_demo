from fastapi import FastAPI
#创建Fastapi实例
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

#路由，创建url和函数的对应关系映射
@app.get("/hello")
async def get_hello():
  return {"msg":"你好FastAPI"}
@app.get("/user/hello")
async def get_learn():
  return {"msg":"我正在学习FastAPI"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("luyou:app", host="0.0.0.0", port=8000, reload=True)