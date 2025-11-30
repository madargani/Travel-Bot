from fastapi import FastAPI

api = FastAPI()

@api.get('/hello')
async def hello():
    return "hello"
