import os
import httpx
from dotenv import load_dotenv

load_dotenv()

BOOKING_BASE_URL = os.getenv("BOOKING_BASE_URL")
BOOKING_HOST = os.getenv("BOOKING_HOST")
BOOKING_KEY = os.getenv("BOOKING_KEY")