"""
Travel Agent Dependencies - Configuration and API keys for Pydantic-AI agent.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class TravelDependencies:
    """Dependencies for the travel agent containing all API keys and configuration."""

    # Flight API (Travelpayouts)
    travelpayouts_token: str
    travelpayouts_marker: str

    # Hotel API (Booking.com via RapidAPI)
    hotels_rapidapi_key: str
    hotels_rapidapi_host: str

    # Restaurant API (Yelp)
    yelp_api_key: str

    # Events API (Ticketmaster)
    ticketmaster_api_key: str

    # Session management
    session_id: str = ""
    message_history: List[Dict[str, Any]] = field(default_factory=list)
    itinerary_progress: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_env(
        cls,
        session_id: str = "",
        message_history: List[Dict[str, Any]] = None,
        itinerary_progress: Dict[str, Any] = None,
    ) -> "TravelDependencies":
        """Create dependencies from environment variables."""
        return cls(
            travelpayouts_token=os.getenv("TRAVELPAYOUTS_TOKEN", ""),
            travelpayouts_marker=os.getenv("TRAVELPAYOUTS_MARKER", ""),
            hotels_rapidapi_key=os.getenv("HOTELS_RAPIDAPI_KEY", ""),
            hotels_rapidapi_host=os.getenv(
                "HOTELS_RAPIDAPI_HOST", "booking-com18.p.rapidapi.com"
            ),
            yelp_api_key=os.getenv("YELP_API_KEY", ""),
            ticketmaster_api_key=os.getenv("TICKETMASTER_API_KEY", ""),
            session_id=session_id,
            message_history=message_history or [],
            itinerary_progress=itinerary_progress or {},
        )
