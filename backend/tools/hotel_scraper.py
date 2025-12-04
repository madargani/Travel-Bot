from dotenv import load_dotenv
from langchain.tools import tool
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import os
import requests
import json

# Load environment variables from .env
load_dotenv()

# Hotel API keys (Booking.com via RapidAPI) – separate from your flight tokens
HOTELS_RAPIDAPI_KEY = os.getenv("HOTELS_RAPIDAPI_KEY")
HOTELS_RAPIDAPI_HOST = os.getenv("HOTELS_RAPIDAPI_HOST", "booking-com18.p.rapidapi.com")

AUTO_COMPLETE_ENDPOINT = f"https://{HOTELS_RAPIDAPI_HOST}/stays/auto-complete"
SEARCH_ENDPOINT = f"https://{HOTELS_RAPIDAPI_HOST}/stays/search"

def get_location_id(city: str) -> Optional[str]:
    """
    Use Booking.com 'auto-complete' endpoint to resolve a city name to a locationId.

    This takes a free-text city name (e.g., 'New York') and asks the API for
    matching locations. We then pick the first match and use its 'locationId'
    field for the main hotel search endpoint.
    """
    if not HOTELS_RAPIDAPI_KEY:
        raise ValueError("HOTELS_RAPIDAPI_KEY environment variable is not set.")

    headers = {
        "x-rapidapi-key": HOTELS_RAPIDAPI_KEY,
        "x-rapidapi-host": HOTELS_RAPIDAPI_HOST,
    }

    params = {
        "text": city,
    }

    resp = requests.get(AUTO_COMPLETE_ENDPOINT, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    # The exact response shape can vary; this is a reasonable guess for Booking.com autocomplete.
    # Adjust if needed after printing data once.
    suggestions = data.get("data") or data.get("results") or []
    if not suggestions:
        return None

    # We assume the first suggestion is the best match
    first = suggestions[0]

    # Some APIs use 'locationId' directly on the suggestion
    location_id = first.get("locationId")
    if location_id:
        return location_id

    # If there's no 'locationId', you may need to construct it from dest_id & dest_type,
    # but for now we just return None so you can see/debug the structure.
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
) -> Dict[str, Any]:
    """
    Call Booking.com stays/search endpoint with a locationId and date range.

    This returns raw JSON from the API, which can contain hotel listings,
    prices, ratings, etc.
    """
    if not HOTELS_RAPIDAPI_KEY:
        raise ValueError("HOTELS_RAPIDAPI_KEY environment variable is not set.")

    headers = {
        "x-rapidapi-key": HOTELS_RAPIDAPI_KEY,
        "x-rapidapi-host": HOTELS_RAPIDAPI_HOST,
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

    resp = requests.get(SEARCH_ENDPOINT, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


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
    results = (
        data.get("stays") or
        data.get("hotels") or
        data.get("results") or
        []
    )

    for h in results[:limit]:
        name = h.get("name") or h.get("hotelName")
        price = None
        currency = None

        price_info = h.get("price") or h.get("priceBreakdown") or {}
        # Try common patterns for price fields
        if isinstance(price_info, dict):
            price = price_info.get("value") or price_info.get("price") or price_info.get("grossPrice")
            currency = price_info.get("currency") or price_info.get("currencyCode")

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
    checkin_date: str = Field(description="Check-in date in 'YYYY-MM-DD', e.g., '2025-12-05'")
    checkout_date: str = Field(description="Check-out date in 'YYYY-MM-DD', e.g., '2025-12-06'")
    adults: Optional[int] = Field(default=2, description="Number of adults, e.g., 2")
    rooms: Optional[int] = Field(default=1, description="Number of rooms, e.g., 1")
    min_price: Optional[int] = Field(default=None, description="Optional minimum price filter")
    max_price: Optional[int] = Field(default=None, description="Optional maximum price filter")
    currency: Optional[str] = Field(default="USD", description="Currency code, e.g., 'USD'")


@tool("hotel_search_tool", args_schema=HotelSearchArgs, return_direct=True)
def hotel_search_tool(
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
    location_id = get_location_id(city)
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
    )

    hotels = summarize_hotels(raw, limit=5)
    if not hotels:
        return f"No hotels found for {city} between {checkin_date} and {checkout_date}."

    # Return as string, like your flight_search_tool
    return str(hotels)


if __name__ == "__main__":
    print("Testing Booking.com hotel search via RapidAPI…")

    test_city = "New York"
    checkin = "2025-12-05"
    checkout = "2025-12-06"

    loc_id = get_location_id(test_city)
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
        )

        hotels = summarize_hotels(raw, limit=5)
        print(f"\nFound {len(hotels)} hotels (summarized):")
        print(json.dumps(hotels, indent=2))
    else:
        print("Could not resolve city to a locationId.")


