import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./fitbuddy.db"
)

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
) or os.getenv(
    "GOOGLE_API_KEY"
)

WORKOUT_MODEL = os.getenv(
    "WORKOUT_MODEL",
    "gemini-3.1-pro-preview"
)

NUTRITION_MODEL = os.getenv(
    "NUTRITION_MODEL",
    "gemini-3.8-flash"
)