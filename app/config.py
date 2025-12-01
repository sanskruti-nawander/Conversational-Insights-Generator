from dotenv import load_dotenv
import os

# Load .env from project root in dev
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.0-flash-lite")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set (check your .env)")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set (check your .env)")
