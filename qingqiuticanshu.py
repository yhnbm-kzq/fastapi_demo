from fastapi import FastAPI,Path,Query
from pydantic import BaseModel,Field

#创建Fastapi实例
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}
class User(BaseModel):
  username:str
  password:str
@app.post("/register/")
async def register(user:User):
  return user
class Book(BaseModel):
  name:str=Field(...,min_length=2,max_length=20)
  author:str=Field(min_length=2,max_length=10)
  publisher:str=Field(default='黑马出版社')
  price:str=Field(...,gt='0')
@app.post("/book/")
async def get_book(book:Book):
  return book
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("qingqiuticanshu:app", host="0.0.0.0", port=8000, reload=True)