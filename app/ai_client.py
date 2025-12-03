import asyncio
from google import genai

from .config import GEMINI_API_KEY, GEMINI_MODEL_NAME
from .models import CallInsight, CallInsightExtended


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





def _call_llm_sync_extended(transcript: str) -> CallInsightExtended:
    """
    Synchronous call to Gemini for extended analysis.
    """
    system_instructions = (
        "You are analyzing debt-collection calls. "
        "Return a structured JSON object with these exact fields:\n"
        "- customer_intent: what the customer plans or wants to do.\n"
        "- sentiment: overall sentiment of the call (Negative, Neutral, Positive).\n"
        "- action_required: true if follow-up is required by the agent.\n"
        "- summary: brief summary of the call.\n"
        "- primary_purpose: the main purpose of the call from the agent's side.\n"
        "- objective_met: boolean, whether the agent's call objective was met.\n"
        "- key_results: list of key outcomes (e.g. promise to pay, settlement request, dispute raised, hardship disclosed).\n"
        "- customer_intentions: describe what the customer intends to do next.\n"
        "- circumstances: summarize important situational context (job loss, accident, salary delay, etc.).\n"
        "- reasons_non_payment: reasons for non-payment, if any (or null).\n"
        "- financial_hardship: description of hardship if mentioned (or null).\n"
        "- start_sentiment: sentiment at the beginning of the call (Negative, Neutral, Positive).\n"
        "- end_sentiment: sentiment at the end of the call (Negative, Neutral, Positive).\n"
        "- agent_performance_rating: integer 1 to 5 based on professionalism, clarity, and empathy.\n"
        "- agent_performance_notes: short justification for the rating.\n"
        "Return JSON strictly matching the given schema."
    )

    prompt = f"{system_instructions}\n\nTranscript:\n{transcript}"

    response = client.models.generate_content(
        model=GEMINI_MODEL_NAME,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": CallInsightExtended,
        },
    )

    insight: CallInsightExtended = response.parsed
    return insight


async def generate_insights_extended(transcript: str) -> CallInsightExtended:
    return await asyncio.to_thread(_call_llm_sync_extended, transcript)

