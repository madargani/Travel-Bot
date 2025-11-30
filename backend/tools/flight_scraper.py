import os
import httpx
import asyncio
import requests
import json
from typing import Optional, Dict, Any, List

TRAVELPAYOUTS_API_TOKEN = os.getenv("TRAVELPAYOUTS_TOKEN")
TRAVELPAYOUTS_MARKER = os.getenv("TRAVELPAYOUTS_MARKER")  # optional for booking links
AVIASALES_BASE = "https://www.aviasales.com"

BASE_URL = "https://api.travelpayouts.com/aviasales/v3/prices_for_dates"
AUTOCOMPLETE_URL = "https://autocomplete.travelpayouts.com/places2"

def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str] = None,
    currency: str = "USD",
) -> Dict[str, Any]:
    if not TRAVELPAYOUTS_API_TOKEN:
        raise ValueError("TRAVELPAYOUTS_TOKEN environment variable is not set.")

    params = {
        "origin": origin,
        "destination": destination,
        "departure_at": departure_date,
        "return_at": return_date,
        "currency": currency,
        "token": TRAVELPAYOUTS_API_TOKEN,
    }

    resp = requests.get(BASE_URL, params=params)
    resp.raise_for_status()
    return resp.json()

def summarize_flights(raw: Dict[str, Any], limit: int = 3) -> List[Dict[str, Any]]:
    flights = raw.get("data", [])
    summaries = []

    for f in flights[:limit]:
        summaries.append({
            "price": f.get("price"),
            "airline": f.get("airline"),
            "origin_airport": f.get("origin_airport"),
            "destination_airport": f.get("destination_airport"),
            "departure_at": f.get("departure_at"),
            "transfers": f.get("transfers"),
            "link": f.get("link"),
        })
    return summaries

def build_booking_url(partial_link: str) -> str:
    """
    Turn a partial '/search/...' path from Travelpayouts into a full Aviasales URL.
    Also attach your marker if it's not already there.
    """
    if not partial_link:
        return ""

    # Make sure it starts with '/'
    if not partial_link.startswith("/"):
        partial_link = "/" + partial_link

    url = AVIASALES_BASE + partial_link

    # Add marker if we have one and it's not already in the URL
    if TRAVELPAYOUTS_MARKER and "marker=" not in url:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}marker={TRAVELPAYOUTS_MARKER}"

    return url

if __name__ == "__main__":
    
    print("Testing Travelpayouts flight search…")
    raw = search_flights("SFO", "SAN", "2025-12-15")
    flights = raw.get("data", [])
    print("Found", len(flights), "results")

    for f in flights[:5]:  # first 5 flights
        print("\n--- Flight ---")
        print(f"Price: ${f.get('price')}")
        print(f"Airline: {f.get('airline')}")
        print(f"Route: {f.get('origin_airport')} → {f.get('destination_airport')}")
        print(f"Departure: {f.get('departure_at')}")
        print(f"Transfers: {f.get('transfers')}")
        full_url = build_booking_url(f.get("link"))
        print(f"Booking URL: {full_url}")


        ## prints out a desired output
        ## uses a data cache so is not live, thinking about changing
        ## but for now it works and will see how it goes
        