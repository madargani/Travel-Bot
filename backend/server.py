"""
FastAPI server for Travel-Bot using Pydantic-AI unified travel agent.
Provides HTTP endpoints for travel planning functionality.
"""

import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from agent_dependencies import TravelDependencies
from travel_agent import travel_agent


# Pydantic models for requests/responses
class ChatRequest(BaseModel):
    message: str
    stream: bool = False


class ChatResponse(BaseModel):
    response: str


# Initialize FastAPI app
app = FastAPI(
    title="Travel-Bot API",
    description="AI-powered travel planning assistant",
    version="1.0.0",
)

# CORS middleware - TODO: Change for production
origins = ["http://localhost:3000", "http://localhost:3001"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize dependencies
deps = TravelDependencies.from_env()


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Travel-Bot API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/chat",
            "chat_stream": "/chat/stream",
            "health": "/health",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "agent_ready": True,
        "dependencies_loaded": bool(deps.travelpayouts_token)
        and bool(deps.hotels_rapidapi_key)
        and bool(deps.yelp_api_key)
        and bool(deps.ticketmaster_api_key),
    }


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Chat endpoint for non-streaming responses.

    Args:
        request: ChatRequest containing message and optional stream flag

    Returns:
        ChatResponse with the agent's response
    """
    try:
        result = await travel_agent.run(request.message, deps=deps)
        return ChatResponse(response=result.output)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent processing error: {str(e)}")


async def response_generator(message: str):
    """
    Async generator for streaming responses from the travel agent.
    """
    try:
        # Use non-streaming for now to avoid complexity
        result = await travel_agent.run(message, deps=deps)

        # Send the complete response as chunks
        words = result.output.split()
        for i, word in enumerate(words):
            if i == len(words) - 1:
                # Last word - send completion
                yield f"data: {json.dumps({'content': word, 'done': True})}\n\n"
            else:
                # Regular chunk
                yield f"data: {json.dumps({'content': word + ' '})}\n\n"

    except Exception as e:
        # Send error message
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


@app.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """
    Streaming chat endpoint using Server-Sent Events.

    Args:
        request: ChatRequest containing message and optional stream flag

    Returns:
        StreamingResponse with real-time agent output
    """
    return StreamingResponse(
        response_generator(request.message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        },
    )


@app.get("/tools")
async def list_tools():
    """
    List all available tools in the travel agent.
    """
    tools = list(travel_agent.toolsets[0].tools.keys())  # pyright: ignore
    return {
        "available_tools": tools,
        "count": len(tools),
        "agent_model": str(travel_agent.model),
        "workflow": "sequential (flights → hotels → activities)",
    }


@app.get("/agent/info")
async def agent_info():
    """
    Get detailed information about the travel agent configuration.
    """
    return {
        "agent_type": "Pydantic-AI Unified Travel Agent",
        "model": str(travel_agent.model),
        "dependencies": {
            "travelpayouts_configured": bool(deps.travelpayouts_token),
            "hotels_api_configured": bool(deps.hotels_rapidapi_key),
            "yelp_api_configured": bool(deps.yelp_api_key),
            "ticketmaster_api_configured": bool(deps.ticketmaster_api_key),
        },
        "capabilities": [
            "flight_search",
            "hotel_search",
            "restaurant_search",
            "event_search",
            "attraction_search",
        ],
        "workflow": {
            "type": "sequential",
            "steps": ["flights", "hotels", "activities"],
            "flexible": True,
            "budget_categories": ["value", "comfort", "premium"],
        },
    }


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting Travel-Bot API Server")
    print(f"📍 Available at: http://localhost:8000")
    print(f"📚 API docs: http://localhost:8000/docs")
    print(f"🔧 Health check: http://localhost:8000/health")

    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
