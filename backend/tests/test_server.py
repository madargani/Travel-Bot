"""Test FastAPI server endpoints."""

import pytest
from fastapi.testclient import TestClient
from server import app


class TestFastAPIServer:
    """Test suite for FastAPI server endpoints."""

    def test_root_endpoint(self):
        """Test root endpoint returns API info."""
        client = TestClient(app)
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "endpoints" in data

    def test_health_endpoint(self):
        """Test health check endpoint."""
        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "agent_ready" in data

    def test_tools_endpoint(self):
        """Test tools discovery endpoint."""
        client = TestClient(app)
        response = client.get("/tools")

        assert response.status_code == 200
        data = response.json()
        assert "available_tools" in data
        assert "count" in data
        assert isinstance(data["available_tools"], list)

    def test_agent_info_endpoint(self):
        """Test agent info endpoint."""
        client = TestClient(app)
        response = client.get("/agent/info")

        assert response.status_code == 200
        data = response.json()
        assert "agent_type" in data
        assert "capabilities" in data
        assert "workflow" in data

    def test_chat_endpoint(self):
        """Test chat endpoint with valid request."""
        client = TestClient(app)
        response = client.post(
            "/chat", json={"message": "Hello! I want to plan a trip."}
        )

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert len(data["response"]) > 0

    def test_chat_endpoint_empty_message(self):
        """Test chat endpoint handles empty message gracefully."""
        client = TestClient(app)
        response = client.post("/chat", json={"message": ""})

        # Should handle gracefully, not error
        assert response.status_code == 200
        data = response.json()
        assert "response" in data

    def test_chat_endpoint_invalid_request(self):
        """Test chat endpoint rejects invalid requests."""
        client = TestClient(app)
        response = client.post("/chat", json={})

        # Should return validation error
        assert response.status_code == 422

    def test_streaming_endpoint(self):
        """Test streaming endpoint."""
        client = TestClient(app)
        response = client.post(
            "/chat/stream", json={"message": "What attractions are in Paris?"}
        )

        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]

        # Should contain streaming data
        assert "data:" in response.text

    def test_streaming_endpoint_empty_message(self):
        """Test streaming endpoint handles empty message."""
        client = TestClient(app)
        response = client.post("/chat/stream", json={"message": ""})

        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
