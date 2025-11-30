from typing import cast

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain.messages import AIMessageChunk
from langchain_core.messages.ai import AIMessage

from agents.agent import agent

api = FastAPI()

# TODO: Change for production
origins = ["http://localhost:3000"]

api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def response_generator(prompt: str):
    async for token, _ in agent.astream(
        {"messages": [{"role": "user", "content": prompt}]}, stream_mode="messages"
    ):
        yield str(cast(AIMessage, token).content)


@api.post("/prompt")
async def hello(prompt: str):
    return StreamingResponse(response_generator(prompt), media_type="text/event-stream")
