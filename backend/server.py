from fastapi import FastAPI

from agents.model_node import llm_call

api = FastAPI()


@api.("/prompt")
async def hello():
    
