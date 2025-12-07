from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import requests
from pydantic_ai import Agent, RunContext
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent_dependencies import TravelDependencies

AVIASALES_BASE = "https://www.aviasales.com"
BASE_URL = "https://api.travelpayouts.com/aviasales/v3/prices_for_dates"


def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str] = None,
    currency: str = "USD",
    travelpayouts_token: str = "",
) -> Dict[str, Any]:
    if not travelpayouts_token:
        raise ValueError("TRAVELPAYOUTS_TOKEN environment variable is not set.")

    params = {
        "origin": origin,
        "destination": destination,
        "departure_at": departure_date,
        "return_at": return_date,
        "currency": currency,
        "token": travelpayouts_token,
    }

    resp = requests.get(BASE_URL, params=params)
    resp.raise_for_status()
    return resp.json()


def summarize_flights(raw: Dict[str, Any], limit: int = 3) -> List[Dict[str, Any]]:
    flights = raw.get("data", [])
    summaries = []

    for f in flights[:limit]:
        summaries.append(
            {
                "origin": f.get("origin"),
                "destination": f.get("destination"),
                "price": f.get("price"),
                "airline": f.get("airline"),
                "departure_at": f.get("departure_at"),
                "return_at": f.get("return_at"),
            }
        )
    return summaries


def build_booking_url(partial_link: str, travelpayouts_marker: str = "") -> str:
    if not partial_link:
        return ""

    if not partial_link.startswith("/"):
        partial_link = "/" + partial_link

    url = AVIASALES_BASE + partial_link

    if travelpayouts_marker and "marker=" not in url:
        separator = "&" if "?" in url else "?"
        url = f"{url}{separator}marker={travelpayouts_marker}"

    return url


# Pydantic schemas for tools
class FlightSearchArgs(BaseModel):
    origin: str = Field(description="IATA code of the origin airport, e.g., 'SFO'")
    destination: str = Field(
        description="IATA code of the destination airport, e.g., 'JFK'"
    )
    departure_date: str = Field(
        description="Departure date in 'YYYY-MM-DD', e.g., '2025-12-15'"
    )
    return_date: Optional[str] = Field(
        default=None, description="Optional return date in 'YYYY-MM-DD'"
    )
    currency: Optional[str] = Field(
        default="USD", description="Currency code, e.g., 'USD'"
    )


class BookingURLArgs(BaseModel):
    partial_link: str = Field(
        description="Partial booking link from Travelpayouts, e.g., '/search/...'"
    )


# Create the flight search agent
flight_agent = Agent(
    "openai:gpt-4o",
    deps_type=TravelDependencies,
    system_prompt="You are a flight search assistant. Use the available tools to search for flights and build booking URLs.",
)


@flight_agent.tool
async def flight_search_tool(
    ctx: RunContext[TravelDependencies],
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str] = None,
    currency: str = "USD",
) -> str:
    """Search for flights between two cities."""
    raw = search_flights(
        origin,
        destination,
        departure_date,
        return_date,
        currency,
        ctx.deps.travelpayouts_token,
    )
    flights = summarize_flights(raw, limit=5)
    return str(flights)


@flight_agent.tool
async def build_booking_url_tool(
    ctx: RunContext[TravelDependencies],
    partial_link: str,
) -> str:
    """Build a full booking URL from a partial link."""
    return build_booking_url(partial_link, ctx.deps.travelpayouts_marker)


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    deps = TravelDependencies.from_env()
    print("Testing Travelpayouts flight search…")
    raw = search_flights(
        "SFO", "SAN", "2025-12-15", travelpayouts_token=deps.travelpayouts_token
    )
    flights = raw.get("data", [])
    print("Found", len(flights), "results")
    for f in flights[:5]:
        print(f)
