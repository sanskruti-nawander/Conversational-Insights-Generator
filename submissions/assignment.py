"""
===========================================
 Conversational Insights Generator
 SINGLE-FILE SUBMISSION (FastAPI + Gemini)
===========================================

This file contains:
- Pydantic models
- Async PostgreSQL setup using asyncpg
- Gemini generate_insights() function (structured JSON)
- FastAPI app with /analyze_call endpoint
- Comment block with CURL example + sample PostgreSQL output

-------------------------------------------
 HOW TO RUN
-------------------------------------------
# Install dependencies:
pip install fastapi uvicorn[standard] asyncpg pydantic python-dotenv google-genai

# Set required environment variables:
set DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/calls_db
set GEMINI_API_KEY=YOUR_KEY
set GEMINI_MODEL_NAME=gemini-2.0-flash-lite

# Start server:
uvicorn assignment:app --reload --port 8000


-------------------------------------------
 CURL EXAMPLE USED FOR TESTING
-------------------------------------------

curl -X POST "http://127.0.0.1:8000/analyze_call" ^
 -H "Content-Type: application/json" ^
 -d "{\"transcript\": \"Agent: Hello, customer: I want to make a payment next week.\"}"

Expected Response:
{
  "id": 1,
  "insights": {
    "customer_intent": "make a payment next week",
    "sentiment": "Neutral",
    "action_required": false,
    "summary": "Customer states their intent to make a payment next week."
  }
}

-------------------------------------------
 SAMPLE POSTGRES SELECT OUTPUT
-------------------------------------------

SELECT id, transcript, intent, sentiment, action_required, summary, created_at
FROM call_records
ORDER BY id;

 id | transcript | intent | sentiment | action_required | summary | created_at
----+------------+--------+-----------+------------------+---------+-------------
 1  | Agent: Hello, customer... | make a payment next week | Neutral | false |
    Customer states intent to pay next week | 2025-12-01 ...

"""

# =====================================================
#                   IMPORTS
# =====================================================

import os
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncpg

# Gemini client
from google import genai

from dotenv import load_dotenv
load_dotenv()



# =====================================================
#                   ENVIRONMENT CONFIG
# =====================================================

DATABASE_URL = os.getenv("DATABASE_URL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.0-flash-lite")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable not set.")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY environment variable not set.")

# Configure Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)


# =====================================================
#                   Pydantic MODELS
# =====================================================

class CallInsight(BaseModel):
    customer_intent: str
    sentiment: str
    action_required: bool
    summary: str


class TranscriptIn(BaseModel):
    transcript: str


# =====================================================
#                DATABASE CONNECTION
# =====================================================

class DB:
    pool: asyncpg.pool.Pool | None = None

db = DB()


async def init_db():
    """
    Initialize PostgreSQL connection pool + create table if not exists.
    """
    if db.pool:
        return

    db.pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)

    async with db.pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS call_records (
                id SERIAL PRIMARY KEY,
                transcript TEXT NOT NULL,
                intent TEXT NOT NULL,
                sentiment TEXT NOT NULL,
                action_required BOOLEAN NOT NULL,
                summary TEXT NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)


# =====================================================
#                GEMINI LLM FUNCTION
# =====================================================

def _call_llm_sync(transcript: str) -> CallInsight:
    """
    Runs Gemini structured output synchronously.
    Wrapped in asyncio.to_thread() for FastAPI async support.
    """
    system_prompt = (
        "You are an expert analyzing customer debt collection calls. "
        "Extract ONLY these fields strictly in JSON:\n"
        "- customer_intent (string)\n"
        "- sentiment ('Negative','Neutral','Positive')\n"
        "- action_required (boolean)\n"
        "- summary (string)\n"
        "Return JSON using the exact schema."
    )

    full_prompt = f"{system_prompt}\n\nTranscript:\n{transcript}"

    # Structured JSON response
    response = client.models.generate_content(
        model=GEMINI_MODEL_NAME,
        contents=full_prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": CallInsight,
        },
    )

    return response.parsed  # directly returns Pydantic model


async def generate_insights(transcript: str) -> CallInsight:
    """
    Async wrapper for Gemini call.
    """
    return await asyncio.to_thread(_call_llm_sync, transcript)


# =====================================================
#                FASTAPI APPLICATION
# =====================================================

app = FastAPI(title="Conversational Insights Generator")


@app.on_event("startup")
async def startup():
    await init_db()


@app.post("/analyze_call")
async def analyze_call(payload: TranscriptIn):
    """
    Accepts a transcript, extracts structured insights via Gemini,
    stores them in PostgreSQL, and returns (id + insights).
    """
    transcript = payload.transcript.strip()
    if not transcript:
        raise HTTPException(status_code=400, detail="Transcript cannot be empty")

    try:
        insights = await generate_insights(transcript)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {e}")

    insert_sql = """
        INSERT INTO call_records (transcript, intent, sentiment, action_required, summary)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id;
    """

    async with db.pool.acquire() as conn:
        async with conn.transaction():
            record_id = await conn.fetchval(
                insert_sql,
                transcript,
                insights.customer_intent,
                insights.sentiment,
                insights.action_required,
                insights.summary,
            )

    return JSONResponse({"id": record_id, "insights": insights.model_dump()})
