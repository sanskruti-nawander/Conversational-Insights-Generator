from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from .db import init_db, db
from .models import TranscriptIn, CallInsight, CallInsightExtended
from .ai_client import generate_insights, generate_insights_extended


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


@app.post("/analyze_call_extended")
async def analyze_call_extended(payload: TranscriptIn):
    """
    Extended analysis:
    - purpose of call
    - if objective was met
    - key results
    - intentions, circumstances, reasons
    - start/end sentiment
    - agent performance rating & notes
    """
    transcript = payload.transcript.strip()
    if not transcript:
        raise HTTPException(status_code=400, detail="Transcript cannot be empty")

    try:
        insight: CallInsightExtended = await generate_insights_extended(transcript)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {e}")

    if db.pool is None:
        raise HTTPException(status_code=500, detail="Database is not initialized")

    insert_sql = """
        INSERT INTO call_records_extended (
            transcript,
            customer_intent,
            sentiment,
            action_required,
            summary,
            primary_purpose,
            objective_met,
            key_results,
            customer_intentions,
            circumstances,
            reasons_non_payment,
            financial_hardship,
            start_sentiment,
            end_sentiment,
            agent_performance_rating,
            agent_performance_notes
        )
        VALUES (
            $1,$2,$3,$4,$5,
            $6,$7,$8,$9,$10,
            $11,$12,$13,$14,$15,$16
        )
        RETURNING id;
    """

    key_results_str = "; ".join(insight.key_results) if insight.key_results else ""

    async with db.pool.acquire() as conn:
        async with conn.transaction():
            record_id = await conn.fetchval(
                insert_sql,
                transcript,
                insight.customer_intent,
                insight.sentiment,
                insight.action_required,
                insight.summary,
                insight.primary_purpose,
                insight.objective_met,
                key_results_str,
                insight.customer_intentions,
                insight.circumstances,
                insight.reasons_non_payment,
                insight.financial_hardship,
                insight.start_sentiment,
                insight.end_sentiment,
                insight.agent_performance_rating,
                insight.agent_performance_notes,
            )

    return JSONResponse(
        {
            "id": record_id,
            "insights": insight.model_dump(),
        }
    )
