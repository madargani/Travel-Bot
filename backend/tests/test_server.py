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
        assert "updated_itinerary_progress" in data
        assert "updated_message_history" in data
        assert len(data["response"]) > 0

    def test_chat_endpoint_empty_message(self):
        """Test chat endpoint handles empty message gracefully."""
        client = TestClient(app)
        response = client.post("/chat", json={"message": ""})

        # Should handle gracefully, not error
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "updated_itinerary_progress" in data
        assert "updated_message_history" in data

    def test_chat_endpoint_with_history(self):
        """Test chat endpoint with message history and progress."""
        client = TestClient(app)
        request_data = {
            "message": "I want to change my flight choice",
            "message_history": [
                {"role": "user", "content": "Plan a trip to NYC"},
                {"role": "assistant", "content": "I found some flight options"},
            ],
            "itinerary_progress": {
                "stage": "flights",
                "flights": {"origin": "LAX", "destination": "JFK"},
            },
            "session_id": "test_session_123",
        }
        response = client.post("/chat", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "updated_itinerary_progress" in data
        assert "updated_message_history" in data
        assert (
            len(data["updated_message_history"]) == 4
        )  # 2 existing + 1 new user + 1 assistant response

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

    def test_streaming_endpoint_with_context(self):
        """Test streaming endpoint with history and progress."""
        client = TestClient(app)
        request_data = {
            "message": "Show me hotels in NYC",
            "message_history": [
                {"role": "user", "content": "Book flight to NYC"},
                {"role": "assistant", "content": "Flight booked for LAX to JFK"},
            ],
            "itinerary_progress": {
                "stage": "hotels",
                "flights": {
                    "origin": "LAX",
                    "destination": "JFK",
                    "departure_date": "2024-06-01",
                },
            },
        }
        response = client.post("/chat/stream", json=request_data)

        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        assert "data:" in response.text

    def test_streaming_endpoint_empty_message(self):
        """Test streaming endpoint handles empty message."""
        client = TestClient(app)
        response = client.post("/chat/stream", json={"message": ""})

        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
