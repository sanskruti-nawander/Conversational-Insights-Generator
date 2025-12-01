import asyncio
from google import genai  # from google-genai package

from .config import GEMINI_API_KEY, GEMINI_MODEL_NAME
from .models import CallInsight

client = genai.Client(api_key=GEMINI_API_KEY)


def _call_llm_sync(transcript: str) -> CallInsight:
    """
    Synchronous call to Gemini using structured output with CallInsight schema.
    Runs in a separate thread via asyncio.to_thread.
    """
    system_instructions = (
        "You are an expert analyzing customer debt collection calls. "
        "Given a single raw call transcript, extract exactly these fields:\n"
        "- customer_intent: what the customer wants or plans to do.\n"
        "- sentiment: one of 'Negative', 'Neutral', 'Positive'.\n"
        "- action_required: boolean, true if follow-up is needed.\n"
        "- summary: short summary of the call.\n"
        "Return output strictly in the provided schema."
    )

    prompt = (
        f"{system_instructions}\n\n"
        f"Transcript:\n{transcript}"
    )

    response = client.models.generate_content(
        model=GEMINI_MODEL_NAME,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": CallInsight,
        },
    )

    insight: CallInsight = response.parsed
    return insight


async def generate_insights(transcript: str) -> CallInsight:
    """
    Async wrapper for FastAPI.
    """
    return await asyncio.to_thread(_call_llm_sync, transcript)
