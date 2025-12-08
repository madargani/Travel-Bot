import json
import os
import sys
from datetime import date, datetime
from typing import Any, Dict, List, Optional

import requests
from pydantic import BaseModel, Field
from pydantic_ai import RunContext

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent_dependencies import TravelDependencies


def validate_dates(checkin_date: str, checkout_date: str) -> bool:
    """
    Validate that check-in and check-out dates are in the future and check-out is after check-in.
    Returns True if valid, raises ValueError if invalid.
    """
    try:
        checkin = datetime.strptime(checkin_date, "%Y-%m-%d").date()
        checkout = datetime.strptime(checkout_date, "%Y-%m-%d").date()
        today = date.today()

        if checkin < today:
            raise ValueError(
                f"Check-in date {checkin_date} is in the past. Today is {today}."
            )

        if checkout <= checkin:
            raise ValueError(
                f"Check-out date {checkout_date} must be after check-in date {checkin_date}."
            )

        return True
    except ValueError as e:
        if "time data" in str(e):
            raise ValueError(f"Invalid date format. Use YYYY-MM-DD format. Error: {e}")
        raise


def get_location_id(
    city: str, hotels_rapidapi_key: str, hotels_rapidapi_host: str
) -> Optional[str]:
    """
    Use Booking.com 'auto-complete' endpoint to resolve a city name to a locationId.

    This takes a free-text city name (e.g., 'New York') and asks the API for
    matching locations. We then pick the first match and use its 'locationId'
    field for the main hotel search endpoint.
    """
    if not hotels_rapidapi_key:
        raise ValueError("HOTELS_RAPIDAPI_KEY environment variable is not set.")

    headers = {
        "x-rapidapi-key": hotels_rapidapi_key,
        "x-rapidapi-host": hotels_rapidapi_host,
    }

    params = {
        "query": city,
    }

    try:
        resp = requests.get(
            f"https://{hotels_rapidapi_host}/stays/auto-complete",
            headers=headers,
            params=params,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.RequestException as e:
        print(f"API request failed for auto-complete: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response text: {e.response.text}")
        return None

    # The exact response shape can vary; this is a reasonable guess for Booking.com autocomplete.
    # Adjust if needed after printing data once.
    suggestions = data.get("data") or data.get("results") or []
    if not suggestions:
        return None

    # We assume the first suggestion is the best match
    first = suggestions[0]

    # Use the encoded 'id' field for the search API
    encoded_id = first.get("id")
    if encoded_id:
        return str(encoded_id)

    # Fallback to dest_id if no encoded id
    dest_id = first.get("dest_id")
    if dest_id:
        return str(dest_id)

    # If there's no location ID, return None
    return None


def search_hotels(
    location_id: str,
    checkin_date: str,
    checkout_date: str,
    adults: int = 2,
    rooms: int = 1,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    currency: str = "USD",
    hotels_rapidapi_key: str = "",
    hotels_rapidapi_host: str = "",
) -> Dict[str, Any]:
    """
    Call Booking.com stays/search endpoint with a locationId and date range.

    This returns raw JSON from the API, which can contain hotel listings,
    prices, ratings, etc.
    """
    if not hotels_rapidapi_key:
        raise ValueError("HOTELS_RAPIDAPI_KEY environment variable is not set.")

    headers = {
        "x-rapidapi-key": hotels_rapidapi_key,
        "x-rapidapi-host": hotels_rapidapi_host,
    }

    params = {
        "locationId": location_id,
        "checkinDate": checkin_date,
        "checkoutDate": checkout_date,
        "sortBy": "price",
        "rooms": str(rooms),
        "adults": str(adults),
        "units": "metric",
        "temperature": "f",
        "currencyCode": currency,
    }

    if min_price is not None:
        params["minPrice"] = str(min_price)
    if max_price is not None:
        params["maxPrice"] = str(max_price)

    try:
        resp = requests.get(
            f"https://{hotels_rapidapi_host}/stays/search",
            headers=headers,
            params=params,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"API request failed for hotel search: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response text: {e.response.text}")
        raise


def summarize_hotels(raw: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
    """
    Take raw Booking.com search results and extract a simple list of hotels.

    Because different versions of the API can structure results differently,
    this uses common patterns. You may need to tweak the keys after you see
    a real response from your account.
    """
    hotels: List[Dict[str, Any]] = []

    # The hotels might live under data.hotels, data.stays, or similar.
    # Here we try a few likely places:
    data = raw.get("data") or raw

    # Handle case where data is already a list
    if isinstance(data, list):
        results = data
    else:
        results = data.get("stays") or data.get("hotels") or data.get("results") or []

    for h in results[:limit]:
        name = h.get("name") or h.get("hotelName")
        price = None
        currency = None

        price_info = h.get("price") or h.get("priceBreakdown") or {}
        # Try common patterns for price fields
        if isinstance(price_info, dict):
            price = (
                price_info.get("value")
                or price_info.get("price")
                or price_info.get("grossPrice")
                or price_info.get("amountRounded")
            )
            currency = price_info.get("currency") or price_info.get("currencyCode")
            # Handle case where price is a dict with amount
            if isinstance(price, dict):
                price = price.get("value") or price.get("amount")

        rating = h.get("rating") or h.get("reviewScore")
        address = h.get("address") or h.get("location") or {}
        address_str = None
        if isinstance(address, dict):
            address_str = ", ".join(
                filter(
                    None,
                    [
                        address.get("street"),
                        address.get("city"),
                        address.get("country"),
                    ],
                )
            )
        else:
            address_str = str(address)

        link = h.get("url") or h.get("bookingUrl")

        hotels.append(
            {
                "name": name,
                "price": price,
                "currency": currency,
                "rating": rating,
                "address": address_str,
                "link": link,
            }
        )

    return hotels


class HotelSearchArgs(BaseModel):
    city: str = Field(description="City name to search hotels in, e.g., 'New York'")
    checkin_date: str = Field(
        description="Check-in date in 'YYYY-MM-DD', e.g., '2025-12-10'"
    )
    checkout_date: str = Field(
        description="Check-out date in 'YYYY-MM-DD', e.g., '2025-12-15'"
    )
    adults: Optional[int] = Field(default=2, description="Number of adults, e.g., 2")
    rooms: Optional[int] = Field(default=1, description="Number of rooms, e.g., 1")
    min_price: Optional[int] = Field(
        default=None, description="Optional minimum price filter"
    )
    max_price: Optional[int] = Field(
        default=None, description="Optional maximum price filter"
    )
    currency: Optional[str] = Field(
        default="USD", description="Currency code, e.g., 'USD'"
    )


# Standalone tool function for direct integration with travel_agent


async def hotel_search_tool(
    ctx: RunContext[TravelDependencies],
    city: str,
    checkin_date: str,
    checkout_date: str,
    adults: int = 2,
    rooms: int = 1,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    currency: str = "USD",
) -> str:
    """
    Search for hotels in a given city and date range using the Booking.com
    RapidAPI (booking-com18). Returns a simplified list of hotel options.

    This is analogous to your flight_search_tool but for stays/hotels.
    """
    # Validate dates before making API calls
    try:
        validate_dates(checkin_date, checkout_date)
    except ValueError as e:
        return f"Date validation error: {e}"

    location_id = get_location_id(
        city, ctx.deps.hotels_rapidapi_key, ctx.deps.hotels_rapidapi_host
    )
    if not location_id:
        return f"No locationId found for city: {city}. Try a different city name."

    raw = search_hotels(
        location_id=location_id,
        checkin_date=checkin_date,
        checkout_date=checkout_date,
        adults=adults,
        rooms=rooms,
        min_price=min_price,
        max_price=max_price,
        currency=currency,
        hotels_rapidapi_key=ctx.deps.hotels_rapidapi_key,
        hotels_rapidapi_host=ctx.deps.hotels_rapidapi_host,
    )

    hotels = summarize_hotels(raw, limit=5)
    if not hotels:
        return f"No hotels found for {city} between {checkin_date} and {checkout_date}."

    # Return as string, like your flight_search_tool
    return str(hotels)


if __name__ == "__main__":
    import os

    from dotenv import load_dotenv

    load_dotenv()

    deps = TravelDependencies.from_env()
    print("Testing Booking.com hotel search via RapidAPI…")

    test_city = "San Francisco"
    checkin = "2025-12-10"
    checkout = "2025-12-15"

    loc_id = get_location_id(
        test_city, deps.hotels_rapidapi_key, deps.hotels_rapidapi_host
    )
    print("LocationId for", test_city, ":", loc_id)

    if loc_id:
        raw = search_hotels(
            location_id=loc_id,
            checkin_date=checkin,
            checkout_date=checkout,
            adults=2,
            rooms=1,
            min_price=0,
            max_price=300,
            currency="USD",
            hotels_rapidapi_key=deps.hotels_rapidapi_key,
            hotels_rapidapi_host=deps.hotels_rapidapi_host,
        )

        hotels = summarize_hotels(raw, limit=5)
        print(f"\nFound {len(hotels)} hotels (summarized):")
        print(json.dumps(hotels, indent=2))
    else:
        print("Could not resolve city to a locationId.")
