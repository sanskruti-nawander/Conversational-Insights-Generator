from typing import Literal, List
from pydantic import BaseModel

Sentiment = Literal["Negative", "Neutral", "Positive"]


class CallInsight(BaseModel):
    customer_intent: str
    sentiment: Sentiment
    action_required: bool
    summary: str


class CallInsightExtended(BaseModel):
    # Keep original fields
    customer_intent: str
    sentiment: Sentiment
    action_required: bool
    summary: str

    # New fields for extended analysis
    primary_purpose: str
    objective_met: bool
    key_results: List[str]
    customer_intentions: str
    circumstances: str
    reasons_non_payment: str | None = None
    financial_hardship: str | None = None
    start_sentiment: Sentiment
    end_sentiment: Sentiment
    agent_performance_rating: int  # 1–5
    agent_performance_notes: str


class TranscriptIn(BaseModel):
    transcript: str
