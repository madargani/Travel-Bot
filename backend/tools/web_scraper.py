"""
generic_scraper.py — Selector-driven scraper tool.

This scraper handles three categories:
- Restaurants (via Yelp API)
- Events (via Ticketmaster API)
- Attractions (Google Places fallback or static list)

It supports filtering using:
- travel dates
- indoor/outdoor preference
- kid/elder friendly activities
- budget range
"""

import json
from typing import List, Optional, Dict
from pydantic_ai import Agent, RunContext
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent_dependencies import TravelDependencies
import requests


def _query_yelp(city: str, limit: int = 10, yelp_api_key: str = "") -> List[Dict]:
    """Internal helper — hit Yelp API."""
    url = "https://api.yelp.com/v3/businesses/search"
    headers = {"Authorization": f"Bearer {yelp_api_key}"}
    params = {"location": city, "limit": limit, "sort_by": "rating"}

    res = requests.get(url, headers=headers, params=params)

    if res.status_code != 200:
        return []

    data = res.json().get("businesses", [])
    clean_output = []

    for r in data:
        clean_output.append(
            {
                "name": r.get("name"),
                "price": r.get("price", "?"),
                "rating": r.get("rating"),
                "address": " ".join(r.get("location", {}).get("display_address", [])),
                "categories": [c["title"] for c in r.get("categories", [])],
                "image": r.get("image_url"),
                "url": r.get("url"),
            }
        )

    return clean_output


def _query_ticketmaster(
    city: str,
    start_date: str,
    end_date: str,
    limit: int = 10,
    ticketmaster_api_key: str = "",
):
    """
    Internal helper — Ticketmaster Discovery search.
    Date format MUST be ISO timestamp: YYYY-MM-DDTHH:MM:SSZ
    """

    url = "https://app.ticketmaster.com/discovery/v2/events.json"
    params = {
        "city": city,
        "apikey": ticketmaster_api_key,
        "size": limit,
        "startDateTime": f"{start_date}T00:00:00Z",
        "endDateTime": f"{end_date}T23:59:59Z",
    }

    res = requests.get(url, params=params)
    if res.status_code != 200:
        return []

    events = res.json().get("_embedded", {}).get("events", [])

    clean = []
    for e in events:
        clean.append(
            {
                "name": e.get("name"),
                "date": e.get("dates", {}).get("start", {}).get("localDate"),
                "venue": e.get("_embedded", {}).get("venues", [{}])[0].get("name"),
                "url": e.get("url"),
                "classification": [c.get("name") for c in e.get("classifications", [])],
            }
        )
    return clean


# BAREBONES attraction fallback — no API required
#

STATIC_ATTRACTIONS = {
    "paris": [
        {"name": "Louvre Museum", "price": 17, "indoor": True},
        {"name": "Eiffel Tower", "price": 25, "indoor": False},
        {"name": "Seine River Cruise", "price": 15, "indoor": False},
    ],
    "new york": [
        {"name": "MOMA", "price": 25, "indoor": True},
        {"name": "Central Park Bike", "price": 10, "indoor": False},
        {"name": "Empire State", "price": 42, "indoor": True},
    ],
}


# Create the web scraper agent
web_agent = Agent(
    "openai:gpt-4o",
    deps_type=TravelDependencies,
    system_prompt="You are a travel activities assistant. Use the available tools to search for restaurants, events, and attractions.",
)


@web_agent.tool
async def search_restaurants(
    ctx: RunContext[TravelDependencies],
    city: str,
    limit: int = 10,
) -> str:
    """
    Find restaurants for a given city (powered by Yelp).

    Args:
        city: The target city (e.g., "New York")
        limit: Max number of results (default 10)

    Returns:
        JSON string list of restaurants with:
        - name
        - price range
        - rating
        - categories
        - address
        - image
        - url
    """
    data = _query_yelp(city, limit, ctx.deps.yelp_api_key)
    return json.dumps(data)


@web_agent.tool
async def search_events(
    ctx: RunContext[TravelDependencies],
    city: str,
    user_start_date: str,
    user_end_date: str,
    limit: int = 8,
) -> str:
    """
    Search live events for travel itinerary (Ticketmaster).

    Args:
        city: Destination city
        user_start_date: YYYY-MM-DD
        user_end_date: YYYY-MM-DD
        limit: number of max events to return

    Returns:
        JSON string list:
        - name
        - date
        - venue
        - url
        - classification
    """
    raw = _query_ticketmaster(
        city, user_start_date, user_end_date, limit, ctx.deps.ticketmaster_api_key
    )
    return json.dumps(raw)


@web_agent.tool
async def search_attractions(
    ctx: RunContext[TravelDependencies],
    city: str,
) -> str:
    """
    Return a simple curated set of attractions.
    Backup when APIs fail or user needs generic suggestions.

    Args:
        city: Name of the city

    Returns:
        JSON of attractions:
        - name
        - price
        - indoor
    """
    key = city.lower()
    if key not in STATIC_ATTRACTIONS:
        return json.dumps([])

    return json.dumps(STATIC_ATTRACTIONS[key])
