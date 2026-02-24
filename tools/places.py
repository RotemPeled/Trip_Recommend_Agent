import requests
from langchain.tools import tool

from config import FOURSQUARE_API_KEY, FOURSQUARE_BASE_URL
from tools.weather import _geocode_city


@tool
def search_places(city: str, category: str) -> str:
    """Search for places and activities at a destination city.

    Use this tool when you need to find things to do, restaurants, attractions,
    or specific activity types at a destination. Returns top-rated places with
    names, categories, addresses, and ratings.

    Args:
        city: The city to search in (e.g., "Innsbruck", "Barcelona", "Tokyo")
        category: A single category to search for. Only ONE category per call. Examples:
            - "ski resort" or "skiing"
            - "beach"
            - "restaurant" or "local food"
            - "museum" or "art gallery"
            - "nightlife" or "bar"
            - "hiking" or "outdoor recreation"
            - "shopping"
            - "spa" or "wellness"
            - "historical site" or "landmark"
    """
    if not FOURSQUARE_API_KEY:
        return "Error: FOURSQUARE_API_KEY is not set. Please add it to your .env file."

    try:
        geo = _geocode_city(city)
    except ValueError as e:
        return str(e)

    headers = {
        "Authorization": f"Bearer {FOURSQUARE_API_KEY}",
        "Accept": "application/json",
        "X-Places-Api-Version": "2025-06-17",
    }
    params = {
        "query": category,
        "ll": f"{geo['latitude']},{geo['longitude']}",
        "radius": 30000,
        "limit": 5,
        "sort": "POPULARITY",
    }

    try:
        resp = requests.get(
            FOURSQUARE_BASE_URL, headers=headers, params=params, timeout=10
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        return f"Foursquare API error: {e}"

    results = data.get("results", [])
    if not results:
        return f"No {category} found in {city}. Try a different category or nearby city."

    lines = [f"Top {category} in {geo['name']}, {geo['country']}:\n"]
    for i, place in enumerate(results, 1):
        name = place.get("name", "Unknown")
        cats = ", ".join(
            c.get("name", "") for c in place.get("categories", [])
        )
        addr = place.get("location", {}).get("formatted_address", "Address not available")
        lines.append(f"  {i}. {name}")
        if cats:
            lines.append(f"     Category: {cats}")
        lines.append(f"     Address: {addr}")

    return "\n".join(lines)
