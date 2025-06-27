from typing import Dict
from pydantic import BaseModel, ValidationError


class TranscriptPayload(BaseModel):
    interaction_id: str
    customer_id: str
    transcript: str


NEGATIVE_KEYWORDS = {"problema", "ayuda", "no funciona", "tarde", "queja"}
POSITIVE_KEYWORDS = {"gracias", "excelente", "solucionado", "perfecto"}


def process_transcript(data: Dict) -> Dict:
    """
    Validates input data and performs sentiment analysis on the transcript.

    The function uses a keyword-based heuristic to classify the sentiment as
    "NEGATIVE", "POSITIVE", or "NEUTRAL" based on the presence of keywords in
    the transcript text.

    Args:
        data (Dict): Input payload containing interaction_id, customer_id,
            and transcript.

    Returns:
        Dict: Enriched payload including the original data and the detected
            sentiment under the 'analysis' key.

    Raises:
        ValueError: If the input data is missing required fields or is invalid.
    """
    try:
        payload = TranscriptPayload(**data)
    except ValidationError as e:
        raise ValueError(f"Invalid input data: {e}")

    transcript = payload.transcript.lower()

    sentiment = "NEUTRAL"
    if any(keyword in transcript for keyword in NEGATIVE_KEYWORDS):
        sentiment = "NEGATIVE"
    elif any(keyword in transcript for keyword in POSITIVE_KEYWORDS):
        sentiment = "POSITIVE"

    return {
        "interaction_id": payload.interaction_id,
        "customer_id": payload.customer_id,
        "transcript": payload.transcript,
        "analysis": {"sentiment": sentiment},
    }
