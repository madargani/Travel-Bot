# Travel-Bot Development Guidelines

## Commands

### Backend (Python/FastAPI)
- **Start dev server**: `cd backend && uv run python server.py`
- **Run server tests**: `cd backend && uv run python test_server.py`
- **Run agent tests**: `cd backend && uv run python test_travel_agent.py`
- **Install dependencies**: `cd backend && uv sync`
- **API docs**: Visit http://localhost:8000/docs
- **Health check**: Visit http://localhost:8000/health

### Frontend (Next.js/TypeScript)
- **Start dev server**: `cd frontend && npm run dev`
- **Build**: `cd frontend && npm run build`
- **Lint**: `cd frontend && npm run lint`
- **Lint fix**: `cd frontend && npm run lint:fix`

## Code Style

### Python Backend
- Use `uv` for dependency management
- Import order: stdlib → third-party → local modules
- Type hints required for all function signatures
- Use Pydantic BaseModel for data validation
- Environment variables via `python-dotenv`
- Pydantic-AI agents with `@agent.tool` decorators
- Use `TravelDependencies.from_env()` for API key management

### TypeScript Frontend
- Next.js with TypeScript (strict mode disabled)
- Functional components with React hooks
- Tailwind CSS for styling
- Interface definitions in `types/` directory
- Import order: React → third-party → local components
- Use explicit return types for functions

### General
- Clean, structured Markdown for all AI responses
- No raw URLs in output - use formatted links
- Environment variables for all secrets/API keys
- Component-based architecture for reusability