"""Test travel agent functionality with pytest."""

import pytest
from unittest.mock import AsyncMock, patch
from travel_agent import travel_agent


class TestTravelAgent:
    """Test suite for unified travel agent."""

    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """Test that travel agent initializes correctly."""
        assert travel_agent.model is not None
        assert travel_agent.deps_type is not None
        assert hasattr(travel_agent, "toolsets")

    @pytest.mark.asyncio
    async def test_tools_available(self):
        """Test that all expected tools are available."""
        tools = list(travel_agent.toolsets[0].tools.keys())
        expected_tools = [
            "flight_search_tool",
            "hotel_search_tool",
            "search_restaurants",
            "search_events",
            "search_attractions",
        ]

        for tool in expected_tools:
            assert tool in tools, f"Missing tool: {tool}"

    @pytest.mark.asyncio
    async def test_flight_search_tool(self, test_deps):
        """Test flight search tool delegation."""
        with patch("tools.flight_scraper.flight_agent.run") as mock_run:
            mock_run.return_value = AsyncMock()
            mock_run.return_value.output = "Flight search results"

            result = await travel_agent.run(
                "Search flights from SFO to NYC", deps=test_deps
            )

            assert "Flight search results" in result.output
            mock_run.assert_called_once()

    @pytest.mark.asyncio
    async def test_hotel_search_tool(self, test_deps):
        """Test hotel search tool delegation."""
        with patch("tools.hotel_scraper.hotel_agent.run") as mock_run:
            mock_run.return_value = AsyncMock()
            mock_run.return_value.output = "Hotel search results"

            result = await travel_agent.run("Search hotels in Paris", deps=test_deps)

            assert "Hotel search results" in result.output
            mock_run.assert_called_once()

    @pytest.mark.asyncio
    async def test_restaurant_search_tool(self, test_deps):
        """Test restaurant search tool delegation."""
        with patch("tools.web_scraper.web_agent.run") as mock_run:
            mock_run.return_value = AsyncMock()
            mock_run.return_value.output = "Restaurant search results"

            result = await travel_agent.run(
                "Search restaurants in Paris", deps=test_deps
            )

            assert "Restaurant search results" in result.output
            mock_run.assert_called_once()

    @pytest.mark.asyncio
    async def test_error_handling(self, test_deps):
        """Test error handling in agent."""
        with patch("tools.flight_scraper.flight_agent.run") as mock_run:
            mock_run.side_effect = Exception("API Error")

            # Should handle errors gracefully
            result = await travel_agent.run("Search flights", deps=test_deps)

            # Agent should still respond, even with tool errors
            assert len(result.output) > 0
