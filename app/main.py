from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from .db import init_db, db
from .models import TranscriptIn, CallInsight
from .ai_client import generate_insights

app = FastAPI(title="Conversational Insights Generator")


@app.on_event("startup")
async def on_startup() -> None:
    await init_db()


@app.post("/analyze_call")
async def analyze_call(payload: TranscriptIn):
    """
    1. Take transcript
    2. Get structured insights from LLM
    3. Save to Postgres
    4. Return id + insights
    """
    transcript = payload.transcript.strip()
    if not transcript:
        raise HTTPException(status_code=400, detail="Transcript cannot be empty")

    try:
        insight: CallInsight = await generate_insights(transcript)
    except Exception as e:
        # In real life you'd log this
        raise HTTPException(status_code=500, detail=f"LLM error: {e}")

    if db.pool is None:
        raise HTTPException(status_code=500, detail="Database is not initialized")

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
                insight.customer_intent,
                insight.sentiment,
                insight.action_required,
                insight.summary,
            )

    return JSONResponse(
        {
            "id": record_id,
            "insights": insight.model_dump(),
        }
    )
