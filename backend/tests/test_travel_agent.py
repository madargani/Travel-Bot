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
        assert len(travel_agent.toolsets) > 0

    @pytest.mark.asyncio
    async def test_tools_configuration(self):
        """Test that tools are properly configured."""
        # Test that agent has toolsets configured
        assert len(travel_agent.toolsets) > 0

        # Test that we can access toolset
        toolset = travel_agent.toolsets[0]
        assert toolset is not None

        # Test that tools are properly configured by checking toolset has get_tools method
        assert hasattr(toolset, "get_tools")

        # Test that agent has expected number of tools by checking imports work
        from tools.flight_scraper import flight_search_tool, build_booking_url_tool
        from tools.hotel_scraper import hotel_search_tool
        from tools.web_scraper import (
            search_restaurants,
            search_events,
            search_attractions,
        )

        # If imports succeed, tools are available
        assert callable(flight_search_tool)
        assert callable(build_booking_url_tool)
        assert callable(hotel_search_tool)
        assert callable(search_restaurants)
        assert callable(search_events)
        assert callable(search_attractions)

    @pytest.mark.asyncio
    async def test_flight_search_integration(self, test_deps):
        """Test flight search tool integration."""
        with patch("tools.flight_scraper.search_flights") as mock_search:
            mock_search.return_value = {
                "data": [{"price": 500, "airline": "Test Airline"}]
            }

            with patch("tools.flight_scraper.summarize_flights") as mock_summarize:
                mock_summarize.return_value = [
                    {"price": 500, "airline": "Test Airline"}
                ]

                result = await travel_agent.run(
                    "Search flights from SFO to NYC departing 2025-12-15",
                    deps=test_deps,
                )

                # Should get a response about flights
                assert len(result.output) > 0
                mock_search.assert_called_once()

    @pytest.mark.asyncio
    async def test_hotel_search_integration(self, test_deps):
        """Test hotel search tool integration."""
        with patch("tools.hotel_scraper.get_location_id") as mock_location:
            mock_location.return_value = "12345"

            with patch("tools.hotel_scraper.search_hotels") as mock_search:
                mock_search.return_value = {"data": {"stays": []}}

                with patch("tools.hotel_scraper.summarize_hotels") as mock_summarize:
                    mock_summarize.return_value = []

                    result = await travel_agent.run(
                        "Search hotels in Paris from 2025-12-10 to 2025-12-15",
                        deps=test_deps,
                    )

                    # Should get a response about hotels
                    assert len(result.output) > 0
                    mock_location.assert_called_once_with(
                        "Paris",
                        test_deps.hotels_rapidapi_key,
                        test_deps.hotels_rapidapi_host,
                    )

    @pytest.mark.asyncio
    async def test_restaurant_search_integration(self, test_deps):
        """Test restaurant search tool integration."""
        with patch("tools.web_scraper._query_yelp") as mock_yelp:
            mock_yelp.return_value = [{"name": "Test Restaurant", "rating": 4.5}]

            result = await travel_agent.run(
                "Search restaurants in Paris", deps=test_deps
            )

            # Should get a response about restaurants
            assert len(result.output) > 0
            mock_yelp.assert_called_once_with("Paris", 10, test_deps.yelp_api_key)

    @pytest.mark.asyncio
    async def test_events_search_integration(self, test_deps):
        """Test events search tool integration."""
        with patch("tools.web_scraper._query_ticketmaster") as mock_events:
            mock_events.return_value = [{"name": "Test Event", "date": "2025-12-15"}]

            result = await travel_agent.run(
                "Search events in Paris from 2025-12-10 to 2025-12-15", deps=test_deps
            )

            # Should get a response about events
            assert len(result.output) > 0
            mock_events.assert_called_once_with(
                "Paris", "2025-12-10", "2025-12-15", 8, test_deps.ticketmaster_api_key
            )

    @pytest.mark.asyncio
    async def test_attractions_search_integration(self, test_deps):
        """Test attractions search tool integration."""
        result = await travel_agent.run("Search attractions in Paris", deps=test_deps)

        # Should get a response about attractions
        assert len(result.output) > 0

    @pytest.mark.asyncio
    async def test_error_handling(self, test_deps):
        """Test error handling in agent."""
        with patch("tools.flight_scraper.search_flights") as mock_search:
            mock_search.side_effect = Exception("API Error")

            # Should handle errors gracefully
            result = await travel_agent.run(
                "Search flights from SFO to NYC", deps=test_deps
            )

            # Agent should still respond, even with tool errors
            assert len(result.output) > 0
