import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.1-8b-instant"

FOURSQUARE_API_KEY = os.getenv("FOURSQUARE_API_KEY")

OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1"
OPEN_METEO_GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FOURSQUARE_BASE_URL = "https://places-api.foursquare.com/places/search"
