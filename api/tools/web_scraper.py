"""
places_events_client.py

Provides:
 - Yelp-backed restaurant search (API-first).
 - Optional OpenTable/RapidAPI placeholder (stubbed).
 - Event scraping from Eventbrite (HTML parsing) for upcoming local events.[still working on thois]

Pattern follows booking_client.py: lookup_* -> search_* -> normalize_* -> find_*.

Environment variables will be used:
 - YELP_API_KEY        (preferred; required for Yelp API calls)
 - OPENTABLE_KEY       (optional; used if you want to enable OpenTable/RapidAPI)
"""

from __future__ import annotations

import os
import httpx
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

# --- Env / config -----------------------------------------------------------
YELP_API_KEY = os.getenv("YELP_API_KEY")
OPENTABLE_KEY = os.getenv("OPENTABLE_KEY")  # optional / placeholder

# Yelp constants
YELP_SEARCH_URL = "https://api.yelp.com/v3/businesses/search"
YELP_BUSINESS_URL = "https://api.yelp.com/v3/businesses/"

# Eventbrite base (we'll scrape the public search pages)
EVENTBRITE_CITY_URL_TEMPLATE = "https://www.eventbrite.com/d/{country}/{city}--events/"

# A simple timeout used for network calls
HTTP_TIMEOUT = 30.0


# ---------------------------
# Helper: safe float parse
# ---------------------------
def _parse_price_to_category(price_text: Optional[str]) -> Optional[str]:
    """
    Convert a Yelp-style price string like "$$" or numeric to a normalized category.
    Returns price category string ("$", "$$", "$$$") or None.
    """
    if not price_text:
        return None
    price_text = price_text.strip()


    # Yelp already returns '$' style; preserve it
    if all(ch == "$" for ch in price_text):
        return price_text
    

    # trying numeric conversion if present
    try:
        val = float(price_text)
        if val < 15:
            return "$"
        if val < 40:
            return "$$"
        return "$$$"
    except Exception:
        return price_text



# Yelp: search & normalize

async def yelp_search_restaurants(
    city: str,
    country: str = "united-states",
    term: str = "restaurants",
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    limit: int = 10, 
    price_levels: Optional[List[int]] = None,  # Yelp uses 1..4 for $..$$$$
    open_at: Optional[int] = None,  # unix timestamp to filter businesses open at time
) -> Dict[str, Any]:
    """
    Search Yelp for businesses in a city. Requires YELP_API_KEY in env.

    Returns raw Yelp JSON response (dict) or raises helpful exceptions.
    """
    if not YELP_API_KEY:
        # Return an informative empty result rather than raising, so caller can fallback gracefully
        return {"businesses": [], "error": "missing_yelp_api_key"}

    headers = {"Authorization": f"Bearer {YELP_API_KEY}"}
    params: Dict[str, Any] = {
        "location": f"{city}, {country.replace('-', ' ')}",
        "term": term,
        "limit": limit,
    }
    if price_levels:
        params["price"] = ",".join(str(p) for p in price_levels)
    if latitude and longitude:
        params["latitude"] = latitude
        params["longitude"] = longitude
    if open_at:
        params["open_at"] = int(open_at)

    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        resp = await client.get(YELP_SEARCH_URL, headers=headers, params=params)
        # Keep errors explicit for debugging
        if resp.status_code != 200:
            return {"businesses": [], "error": f"yelp_status_{resp.status_code}", "raw_text": resp.text}
        return resp.json()


def normalize_yelp_restaurants(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert Yelp raw response into normalized schema:
    {
      "restaurants": [
        {
          "id", "name", "rating", "review_count", "price_category",
          "address", "city", "country", "phone", "categories", "latitude",
          "longitude", "url"
        }, ...
      ]
    }
    """
    businesses = raw.get("businesses") or []
    out: List[Dict[str, Any]] = []
    for b in businesses:
        out.append({
            "id": b.get("id"),
            "name": b.get("name"),
            "rating": b.get("rating"),
            "review_count": b.get("review_count"),
            "price_category": _parse_price_to_category(b.get("price")),
            "address": " ".join(b.get("location", {}).get("display_address", [])) or None,
            "city": b.get("location", {}).get("city"),
            "country": b.get("location", {}).get("country"),
            "phone": b.get("display_phone"),
            "categories": [c.get("title") for c in (b.get("categories") or [])],
            "latitude": b.get("coordinates", {}).get("latitude"),
            "longitude": b.get("coordinates", {}).get("longitude"),
            "url": b.get("url"),
        })
    return {"restaurants": out}


async def find_restaurants_for_city(
    city: str,
    country: str = "united-states",
    limit: int = 10,
    price_levels: Optional[List[int]] = None,
    term: str = "restaurants",
    open_at: Optional[int] = None,
) -> Dict[str, Any]:
    """
    convenience wrapper: to search Yelp and return normalized restaurants list.
falls back cleanly to empty list + meta if Yelp key missing.
    """
    raw = await yelp_search_restaurants(
        city=city,
        country=country,
        term=term,
        limit=limit,
        price_levels=price_levels,
        open_at=open_at,
    )
    if raw.get("error"):
        return {"restaurants": [], "meta": {"city": city, "reason": raw.get("error")}}
    return normalize_yelp_restaurants(raw)



# Eventbrite scraping (events)


def _parse_event_date_from_text(text: str) -> Optional[datetime]:
    """
    Try simple parsing for Eventbrite-style date texts.
    Eventbrite shows a variety of formats. We'll might have to attempt several patterns,
    but this function intentionally is permissive: returns None if can't parse.
    """
    text = (text or "").strip()



    # Common patterns on Eventbrite snippet: "Sat, Nov 23, 7:00 PM"
    known_formats = [
        "%a, %b %d, %I:%M %p",
        "%b %d, %Y, %I:%M %p",
        "%b %d, %I:%M %p",
        "%B %d, %Y",
        "%b %d, %Y"
    ]
    from dateutil import parser as dateparser  # dateutil is generally available; safe fallback
    try:



        # dateutil.parse is robust for many human-readable forms
        dt = dateparser.parse(text, fuzzy=True)
        return dt   
    
    except Exception:
        for fmt in known_formats:
            try:
                return datetime.strptime(text, fmt)
            except Exception:
                continue
    return None


async def scrape_eventbrite_events(
    city: str,
    country: str = "united-states",
    user_date: Optional[datetime] = None,
    prefer_indoor: Optional[bool] = None,
    has_kids_or_elders: bool = False,
    budget_per_event: Optional[float] = None,
    max_events: int = 10,
) -> Dict[str, Any]:
    """
    Scrape Eventbrite public city listing page for upcoming events.
    Returns {"events": [...], "meta": {...}}

    Note :
      - eventbrite structure might change, not sure yet; selectors are defensive
      - only returns events whose parsed date >= user_date, if it was providedby the uploders
      - price and indoor/outdoor are heuristics from text.
      -

    """


    url = EVENTBRITE_CITY_URL_TEMPLATE.format(country=country, city=city)
    events: List[Dict[str, Any]] = []

    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        resp = await client.get(url, headers={"User-Agent": "TripAI/1.0"})
        if resp.status_code != 200:
            return {"events": [], "meta": {"city": city, "reason": f"eventbrite_status_{resp.status_code}"}}
        html = resp.text

    soup = BeautifulSoup(html, "html.parser")

    # Event listing containers vary, common class on Eventbrite search results:
    # try a few selectors to be robust
    selectors = [
        "div.search-event-card-wrapper",
        "div.eds-event-card-content__content",
        "div.js-search-result"
    ]
    cards = []
    for sel in selectors:
        found = soup.select(sel)
        if found:
            cards = found
            break

    for card in cards:
        if len(events) >= max_events:
            break
        try:
            title_el = card.select_one("div.eds-event-card-content__primary-content a") or card.select_one("a.eds-event-card-content__action-link")
            title = title_el.get_text(strip=True) if title_el else (card.select_one("h3") and card.select_one("h3").get_text(strip=True))
            link = title_el["href"] if title_el and title_el.has_attr("href") else None

            date_el = card.select_one("div.eds-event-card-content__sub") or card.select_one(".eds-text-bs--fixed")
            date_text = date_el.get_text(" ", strip=True) if date_el else None
            parsed_date = _parse_event_date_from_text(date_text) if date_text else None

            # skip past events if user_date provided
            if user_date and parsed_date and parsed_date.date() < user_date.date():
                continue

            # price heuristics (Eventbrite often shows "Free" or "$20")
            price_text = None
            price_candidate = card.select_one(".eds-event-card-content__sub .eds-text-color--ui-800")
            if price_candidate:
                price_text = price_candidate.get_text(strip=True)
            # fallback
            if not price_text:
                pt = card.select_one(".eds-text-bs")
                price_text = pt.get_text(strip=True) if pt else None

            # normalize a numeric price if present
            price_val: Optional[float] = None
            if price_text:
                # look for $xx pattern
                import re
                m = re.search(r"\$\s*([0-9]+(?:\.[0-9]{1,2})?)", price_text)
                if m:
                    try:
                        price_val = float(m.group(1))
                    except:
                        price_val = None
                elif "free" in price_text.lower():
                    price_val = 0.0

            if budget_per_event is not None and price_val is not None and price_val > budget_per_event:
                continue

            # indoor/outdoor heuristics from text
            text_blob = card.get_text(" ").lower()
            is_indoor = any(k in text_blob for k in ["museum", "gallery", "theatre", "indoor", "hall"])
            is_outdoor = any(k in text_blob for k in ["park", "outdoor", "plaza", "beach", "garden", "trail"])

            if prefer_indoor is True and not is_indoor:
                continue
            if prefer_indoor is False and not is_outdoor:
                continue

            # family-friendly heuristic
            if has_kids_or_elders and any(k in text_blob for k in ["18+", "21+", "nightlife", "bar", "pub", "club"]):
                continue

            events.append({
                "title": title,
                "link": link,
                "date_text": date_text,
                "date": parsed_date.isoformat() if parsed_date else None,
                "price_text": price_text,
                "price_value": price_val,
                "is_indoor": is_indoor,
                "is_outdoor": is_outdoor,
            })
        except Exception:
            # skip malformed card
            continue

    return {"events": events, "meta": {"city": city, "source": "eventbrite"}}


async def find_events_for_city(
    city: str,
    country: str = "united-states",
    user_date: Optional[datetime] = None,
    prefer_indoor: Optional[bool] = None,
    has_kids_or_elders: bool = False,
    budget_per_event: Optional[float] = None,
    max_events: int = 6,
) -> Dict[str, Any]:
    """
convenience wrapper to get normalized events for a city.
    """
    raw = await scrape_eventbrite_events(
        city=city,
        country=country,
        user_date=user_date,
        prefer_indoor=prefer_indoor,
        has_kids_or_elders=has_kids_or_elders,
        budget_per_event=budget_per_event,
        max_events=max_events, 
    )
    return raw



# example usage (demo)

if __name__ == "__main__":
    import json
    async def _demo():

        # demo: restaurants (Yelp) - requires YELP_API_KEY in .env
        restaurants = await find_restaurants_for_city(city="San Francisco", country="united-states", limit=5)
         print("=== Restaurants ===")
         print(json.dumps(restaurants, indent=2, default=str))

        # demo: events (Eventbrite scrape) - no API key required
        events = await find_events_for_city(
            city="san-francisco",
            country="united-states",
            user_date=datetime.utcnow(),
            prefer_indoor=None,
            has_kids_or_elders=False,
            budget_per_event=50.0,
            max_events=5
        )
        print("\n=== Events ===")
        print(json.dumps(events, indent=2, default=str))

    asyncio.run(_demo())


# think whether i should caffold a FastAPI 
# route GET /api/places?city=... and GET /api/events?city=... 
# that directly exposes these functions to the frontend or 
# add unit tests (sample HTML + sample Yelp JSON) so then the project can run CI