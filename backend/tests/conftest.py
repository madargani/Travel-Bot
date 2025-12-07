"""
Test configuration for pytest.
"""

import pytest
import os
import sys

# Add backend to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_dependencies import TravelDependencies


@pytest.fixture
def test_deps():
    """Fixture providing test dependencies."""
    return TravelDependencies(
        travelpayouts_token="test_token",
        travelpayouts_marker="test_marker",
        hotels_rapidapi_key="test_hotel_key",
        hotels_rapidapi_host="test.api.com",
        yelp_api_key="test_yelp_key",
        ticketmaster_api_key="test_ticketmaster_key",
    )


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Fixture to mock environment variables."""
    env_vars = {
        "TRAVELPAYOUTS_TOKEN": "test_token",
        "TRAVELPAYOUTS_MARKER": "test_marker",
        "HOTELS_RAPIDAPI_KEY": "test_hotel_key",
        "HOTELS_RAPIDAPI_HOST": "test.api.com",
        "YELP_API_KEY": "test_yelp_key",
        "TICKETMASTER_API_KEY": "test_ticketmaster_key",
    }

    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)

    return env_vars
