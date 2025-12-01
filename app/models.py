from typing import Literal
from pydantic import BaseModel


class CallInsight(BaseModel):
    customer_intent: str
    sentiment: Literal["Negative", "Neutral", "Positive"]
    action_required: bool
    summary: str


class TranscriptIn(BaseModel):
    transcript: str
