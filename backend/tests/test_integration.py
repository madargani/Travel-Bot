"""Integration test for complete Travel-Bot backend."""

import pytest
from fastapi.testclient import TestClient
from server import app


class TestIntegration:
    """Integration tests for complete backend system."""

    def test_complete_travel_workflow(self):
        """Test complete travel planning workflow through API."""
        client = TestClient(app)

        # Test sequential workflow
        workflow_messages = [
            "I want to plan a trip from San Francisco to Paris for December 15-22, 2025.",
            "Let's search for flights first.",
            "Now find hotels in Paris for those dates.",
            "What restaurants can I try in Paris?",
            "What attractions should I visit?",
        ]

        for message in workflow_messages:
            response = client.post("/chat", json={"message": message})
            assert response.status_code == 200
            data = response.json()
            assert "response" in data
            assert len(data["response"]) > 10  # Should have meaningful response

    def test_all_endpoints_accessible(self):
        """Test that all endpoints are accessible."""
        client = TestClient(app)

        endpoints = [
            ("/", "GET"),
            ("/health", "GET"),
            ("/tools", "GET"),
            ("/agent/info", "GET"),
            ("/chat", "POST"),
            ("/chat/stream", "POST"),
        ]

        for endpoint, method in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint, json={"message": "test"})

            assert response.status_code == 200

    def test_streaming_functionality(self):
        """Test streaming endpoint functionality."""
        client = TestClient(app)
        response = client.post(
            "/chat/stream", json={"message": "Tell me about Paris attractions."}
        )

        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]

        # Should contain multiple streaming chunks
        chunks = response.text.split("data: ")
        assert len(chunks) > 5

    def test_error_handling(self):
        """Test error handling across endpoints."""
        client = TestClient(app)

        # Test empty message handling
        response = client.post("/chat", json={"message": ""})
        assert response.status_code == 200  # Should handle gracefully

        # Test malformed request
        response = client.post("/chat", json={})
        assert response.status_code == 422  # Validation error
