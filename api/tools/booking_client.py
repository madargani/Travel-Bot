
#Working out some kinks still
#trying to get it to print a nice json example so it can be read easy




import os
import httpx
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

BOOKING_BASE_URL = os.getenv("BOOKING_BASE_URL")
BOOKING_HOST = os.getenv("BOOKING_HOST")
BOOKING_KEY = os.getenv("BOOKING_KEY")

if not BOOKING_KEY:
    raise RuntimeError("Missing BOOKING_KEY in .env") 

async def lookup_destination_id(query: str, locale: str = "en-us") -> dict:
    """"
    Return a destination object (contains dest_id) for a city name.
    Tries two common endpoints used by RapidAPI providers.
    """
    headers = {"x-rapidapi-host": BOOKING_HOST, "x-rapidapi-key": BOOKING_KEY}
    params  = {"query": query, "locale": locale}

    async with httpx.AsyncClient(timeout=30.0) as client:
        url = f"{BOOKING_BASE_URL.rstrip('/')}/api/v1/hotels/searchDestination"
        resp = await client.get(url, headers=headers, params=params)

        if resp.status_code == 404:
            url = f"{BOOKING_BASE_URL.rstrip('/')}/api/v1/hotels/locations"
            resp = await client.get(url, headers=headers, params=params)

        resp.raise_for_status()
        data = resp.json()

    if isinstance(data, list) and data:
        return data[0]
    if isinstance(data, dict):
        items = data.get("data")
        if isinstance(items, list) and items:
            return items[0]
    return {}

async def search_hotels(
    dest_id: str,
    checkin_date: str,       # "YYYY-MM-DD"
    checkout_date: str,      # "YYYY-MM-DD"
    people: int = 2,         # simplified: treat total people as 'adults'
    rooms: int = 1,
    order_by: str = "price", # "price" | "popularity" | "review_score"
    currency_code: str = "USD",
    page_number: int = 1,
) -> Dict[str, Any]:

    headers = {"x-rapidapi-host": BOOKING_HOST, "x-rapidapi-key": BOOKING_KEY}
    params = {
        "dest_id": dest_id,
        "checkin_date": checkin_date,
        "checkout_date": checkout_date,
        "adults": people,          # simplified mapping
        "rooms": rooms,
        "order_by": order_by,
        "currency_code": currency_code,
        "page_number": page_number,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        url = f"{BOOKING_BASE_URL.rstrip('/')}/api/v1/hotels/searchHotels"
        resp = await client.get(url, headers=headers, params=params)
        resp.raise_for_status()
        return resp.json()
    
def normalize_hotels(raw: dict) -> dict:
    """
    Convert varying Booking raw JSON into a tidy, stable schema your bot can rely on.
    Output shape:
      {"hotels": [{"name", "price", "currency", "rating", "address", "link"}]}
    """
    items: List[dict] = []

    # Try common containers:
    candidates = raw.get("results") or raw.get("data") or raw.get("hotels") or []
    if isinstance(candidates, dict):
        candidates = candidates.get("hotels", [])

    for h in candidates if isinstance(candidates, list) else []:
        name     = h.get("name") or h.get("hotel_name")
        price    = (h.get("price_breakdown") or {}).get("gross_price") or h.get("price")
        currency = (h.get("price_breakdown") or {}).get("currency") or raw.get("currency_code") or "USD"
        rating   = h.get("review_score") or h.get("rating")
        address  = h.get("address") or h.get("location") or {}
        link     = h.get("url") or h.get("booking_url")

        items.append({
            "name": name,
            "price": price,
            "currency": currency,
            "rating": rating,
            "address": address,
            "link": link,
        })

    return {"hotels": items}

async def find_hotels_for_city(
    city: str,
    checkin_date: str,
    checkout_date: str,
    people: int = 2,
    rooms: int = 1,
    order_by: str = "price",
    currency_code: str = "USD",
    locale: str = "en-us",
) -> dict:
    """
    Single call your chat agent can use:
      city name in, stable hotel list out.
    """
    dest = await lookup_destination_id(city, locale=locale)
    dest_id = dest.get("dest_id") or dest.get("id") or dest.get("destination_id")
    if not dest_id:
        return {"hotels": [], "meta": {"city": city, "reason": "dest_id_not_found"}}

    raw = await search_hotels(
        dest_id=dest_id,
        checkin_date=checkin_date,
        checkout_date=checkout_date,
        people=people,
        rooms=rooms,
        order_by=order_by,
        currency_code=currency_code,
        page_number=1,
    )

    print("DEBUG dest:", dest)                  # shows the destination object (should include some id)
    print("DEBUG raw top-level keys:", list(raw.keys()))
    return normalize_hotels(raw)

if __name__ == "__main__":
    import asyncio
    async def _demo():
        hotels = await find_hotels_for_city(
            city="New York",
            checkin_date="2025-12-10",
            checkout_date="2025-12-12",
            people=2,
            rooms=1,
            order_by="price",
            currency_code="USD",
        )
        print(hotels)
    asyncio.run(_demo())