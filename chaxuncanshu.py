from fastapi import FastAPI,Path,Query
#创建Fastapi实例
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}
@app.get("/newslist/")
async def get_newslist(
  skip:int=Query(0,le=100,description="跳过多少条"),
  limit:int=10):
  return {"skip":skip,"limit":limit}
@app.get("/books/")
async def get_book(
  fenlei:str=Query("Python开发",min_length=5,max_length=255),
  price:int=Query(...,ge=50,le=100)):
  return {"fenlei":fenlei,"price":price}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("chaxuncanshu:app", host="0.0.0.0", port=8000, reload=True)