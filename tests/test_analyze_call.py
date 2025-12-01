import pytest
from httpx import AsyncClient, ASGITransport

from app.db import init_db, db
from app.models import CallInsight
import app.main as main  # important: import main module


@pytest.mark.asyncio
async def test_analyze_call_endpoint(monkeypatch):
    # 1) Fake LLM so we don’t hit Gemini during test
    async def fake_generate_insights(transcript: str) -> CallInsight:
        return CallInsight(
            customer_intent="Wants to pay next week",
            sentiment="Neutral",
            action_required=True,
            summary="Customer will pay next week, follow-up required.",
        )

    # Patch the function where it's actually used (in main)
    monkeypatch.setattr(main, "generate_insights", fake_generate_insights)

    # 2) Make sure DB and table exist
    await init_db()
    assert db.pool is not None

    # 3) Use ASGITransport with FastAPI app
    transport = ASGITransport(app=main.app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/analyze_call",
            json={"transcript": "Agent: Hello. Customer: I will pay next week."},
        )

    # 4) Assertions
    assert resp.status_code == 200
    data = resp.json()

    assert "id" in data
    assert isinstance(data["id"], int)

    insights = data["insights"]
    # Now this should be exactly from fake_generate_insights
    assert insights["customer_intent"] == "Wants to pay next week"
    assert insights["sentiment"] == "Neutral"
    assert insights["action_required"] is True
    assert "summary" in insights
    assert insights["summary"] == "Customer will pay next week, follow-up required."
