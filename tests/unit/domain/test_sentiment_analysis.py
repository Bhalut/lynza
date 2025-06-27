import pytest
from app.domain.sentiment_analysis import process_transcript


def test_process_transcript_detects_negative_sentiment():
    """
    Should return sentiment 'NEGATIVE' when transcript contains negative
    keywords.
    """
    data = {
        "interaction_id": "CHAT-1",
        "customer_id": "CUST-1",
        "transcript": "Tengo un problema y necesito ayuda urgente",
    }

    result = process_transcript(data)

    assert result["analysis"]["sentiment"] == "NEGATIVE"


def test_process_transcript_detects_positive_sentiment():
    """
    Should return sentiment 'POSITIVE' when transcript contains positive
    keywords.
    """
    data = {
        "interaction_id": "CHAT-2",
        "customer_id": "CUST-2",
        "transcript": "Gracias, excelente servicio. Pedido solucionado",
    }

    result = process_transcript(data)

    assert result["analysis"]["sentiment"] == "POSITIVE"


def test_process_transcript_detects_neutral_sentiment():
    """
    Should return sentiment 'NEUTRAL' when no known keywords are found.
    """
    data = {
        "interaction_id": "CHAT-3",
        "customer_id": "CUST-3",
        "transcript": "Solo quiero confirmar el estado del pedido",
    }

    result = process_transcript(data)

    assert result["analysis"]["sentiment"] == "NEUTRAL"


def test_process_transcript_raises_value_error_with_invalid_input():
    """
    Should raise ValueError when required fields are missing in input data.
    """
    invalid_data = {
        "interaction_id": "CHAT-4",
        "transcript": "missing customer_id",
    }

    with pytest.raises(ValueError, match="Invalid input data"):
        process_transcript(invalid_data)
