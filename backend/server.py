from fastapi import FastAPI

from agents.agent import agent

api = FastAPI()


@api.post("/prompt")
async def hello(prompt: str):
    return agent.invoke({"messages": [{"role": "user", "content": prompt}]})
