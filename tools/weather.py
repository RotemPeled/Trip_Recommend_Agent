import requests
from langchain.tools import tool

from config import OPEN_METEO_GEOCODING_URL

CLIMATE_API_URL = "https://climate-api.open-meteo.com/v1/climate"
CLIMATE_MODEL = "EC_Earth3P_HR"


def _geocode_city(city: str, country: str | None = None) -> dict:
    """Resolve a city name to coordinates using Open-Meteo geocoding API."""
    params = {"name": city, "count": 5, "language": "en", "format": "json"}
    resp = requests.get(OPEN_METEO_GEOCODING_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if "results" not in data or not data["results"]:
        raise ValueError(f"City '{city}' not found. Please check the spelling.")

    results = data["results"]
    if country:
        country_lower = country.lower()
        filtered = [
            r for r in results
            if r.get("country", "").lower() == country_lower
            or r.get("country_code", "").lower() == country_lower
        ]
        if filtered:
            results = filtered

    best = results[0]
    return {
        "name": best["name"],
        "country": best.get("country", ""),
        "latitude": best["latitude"],
        "longitude": best["longitude"],
    }


def validate_city(city: str, country: str | None = None) -> dict | None:
    """Validate that a city exists. Returns geocoding result or None."""
    try:
        return _geocode_city(city, country)
    except (ValueError, requests.RequestException):
        return None


@tool
def get_weather(city: str, country: str, month: int) -> str:
    """Get average climate data for a city in a specific month.

    Use this tool when you need to check weather conditions at a destination
    for a particular time of year. Returns temperature, precipitation, and
    snowfall data to help evaluate if a destination is suitable.

    Args:
        city: The city name (e.g., "Innsbruck", "Barcelona", "Tokyo")
        country: The country name (e.g., "Austria", "Spain", "Japan")
        month: The month number (1-12, where 1=January, 12=December)
    """
    try:
        geo = _geocode_city(city, country)
    except ValueError as e:
        return str(e)

    import calendar
    last_day = calendar.monthrange(2024, month)[1]
    start_date = f"2024-{month:02d}-01"
    end_date = f"2024-{month:02d}-{last_day:02d}"

    params = {
        "latitude": geo["latitude"],
        "longitude": geo["longitude"],
        "start_date": start_date,
        "end_date": end_date,
        "models": CLIMATE_MODEL,
        "daily": "temperature_2m_mean,temperature_2m_max,temperature_2m_min,precipitation_sum,snowfall_sum",
    }
    try:
        resp = requests.get(CLIMATE_API_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        return f"Weather API error for {city}: {e}"

    daily = data.get("daily", {})
    temps_mean = [t for t in daily.get("temperature_2m_mean", []) if t is not None]
    temps_max = [t for t in daily.get("temperature_2m_max", []) if t is not None]
    temps_min = [t for t in daily.get("temperature_2m_min", []) if t is not None]
    precip = [p for p in daily.get("precipitation_sum", []) if p is not None]
    snow = [s for s in daily.get("snowfall_sum", []) if s is not None]

    avg_temp = round(sum(temps_mean) / len(temps_mean), 1) if temps_mean else "N/A"
    max_temp = round(max(temps_max), 1) if temps_max else "N/A"
    min_temp = round(min(temps_min), 1) if temps_min else "N/A"
    total_precip = round(sum(precip), 1) if precip else "N/A"
    total_snow = round(sum(snow), 1) if snow else "N/A"

    month_names = [
        "", "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ]

    return (
        f"Climate data for {geo['name']}, {geo['country']} in {month_names[month]}:\n"
        f"  Average Temperature: {avg_temp}°C\n"
        f"  Max Temperature: {max_temp}°C\n"
        f"  Min Temperature: {min_temp}°C\n"
        f"  Total Precipitation: {total_precip} mm\n"
        f"  Total Snowfall: {total_snow} cm\n"
    )
