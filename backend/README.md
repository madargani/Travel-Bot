# Travel-Bot Backend

## 🎯 Overview

Production-ready backend for Travel-Bot featuring:
- **Unified Pydantic-AI Agent**: Single travel planning assistant
- **FastAPI Server**: RESTful API with streaming support
- **Tool Delegation**: Clean architecture with specialized agents
- **Comprehensive Testing**: Full test coverage

## 🚀 Quick Start

### Prerequisites
```bash
# Install dependencies
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Development Server
```bash
# Start with auto-reload
uv run python server.py

# Server will be available at:
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
# Health: http://localhost:8000/health
```

### Testing
```bash
# Run all tests
uv run pytest tests/

# Run specific test file
uv run pytest tests/test_server.py

# Run integration tests
uv run pytest tests/test_integration.py
```

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| GET | `/tools` | Available tools |
| GET | `/agent/info` | Agent capabilities |
| POST | `/chat` | Simple chat |
| POST | `/chat/stream` | Streaming chat |

## 🧪 Testing

### Test Structure
```
tests/
├── conftest.py              # Pytest configuration
├── test_travel_agent.py      # Agent functionality tests
├── test_server.py           # FastAPI endpoint tests
├── test_integration.py       # Full integration tests
└── example_usage.py         # Usage examples
```

### Running Tests
```bash
# All tests
uv run pytest tests/ -v

# Coverage report
uv run pytest tests/ --cov=. --cov-report=html

# Specific test
uv run pytest tests/test_server.py::TestFastAPIServer::test_health_endpoint -v
```

## 🏗️ Architecture

### Agent Structure
```
travel_agent.py              # Main unified agent
├── Flight Tools → flight_agent
├── Hotel Tools → hotel_agent
└── Activity Tools → web_agent
```

### Server Structure
```
server.py                   # FastAPI application
├── CORS middleware           # Frontend integration
├── Error handling           # Graceful degradation
├── Health monitoring        # Service status
└── Streaming support        # Real-time responses
```

## 🔧 Configuration

### Environment Variables
```bash
# Required API Keys
TRAVELPAYOUTS_TOKEN=your_token_here
TRAVELPAYOUTS_MARKER=your_marker_here
HOTELS_RAPIDAPI_KEY=your_hotels_key_here
YELP_API_KEY=your_yelp_key_here
TICKETMASTER_API_KEY=your_ticketmaster_key_here

# Optional
HOTELS_RAPIDAPI_HOST=booking-com18.p.rapidapi.com
```

### Dependencies
- **pydantic-ai**: AI agent framework
- **fastapi**: Web framework
- **uvicorn**: ASGI server
- **python-dotenv**: Environment management
- **requests**: HTTP client
- **pytest**: Testing framework

## 📊 Monitoring

### Health Check Response
```json
{
  "status": "healthy",
  "agent_ready": true,
  "dependencies_loaded": true
}
```

### Agent Capabilities
```json
{
  "agent_type": "Pydantic-AI Unified Travel Agent",
  "capabilities": [
    "flight_search",
    "hotel_search",
    "restaurant_search",
    "event_search",
    "attraction_search"
  ],
  "workflow": {
    "type": "sequential",
    "steps": ["flights", "hotels", "activities"],
    "flexible": true
  }
}
```

## 🚀 Deployment

### Production Server
```bash
# Start production server
uvicorn server:app --host 0.0.0.0 --port 8000

# With workers
uvicorn server:app --host 0.0.0.0 --port 8000 --workers 4
```

### Environment Setup
```bash
# Production environment
export ENVIRONMENT=production
export LOG_LEVEL=INFO

# Development environment
export ENVIRONMENT=development
export LOG_LEVEL=DEBUG
```

## 📚 Documentation

- **API Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🔍 Debugging

### Common Issues
1. **Import Errors**: Ensure you're in the `backend/` directory
2. **API Keys**: Check environment variables are set
3. **Port Conflicts**: Ensure port 8000 is available
4. **Dependency Issues**: Run `uv sync` to install packages

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
uv run python server.py
```

## 🎉 Success Metrics

- ✅ **100% Tool Coverage**: All travel capabilities available
- ✅ **Clean Architecture**: Maintainable and extensible
- ✅ **Production Ready**: Error handling, monitoring complete
- ✅ **Comprehensive Testing**: Unit, integration, and endpoint tests
- ✅ **API Standards**: RESTful design with proper HTTP codes
- ✅ **Documentation**: Complete API docs and examples

The Travel-Bot backend is production-ready for frontend integration and deployment!