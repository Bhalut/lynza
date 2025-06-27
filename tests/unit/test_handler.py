import pytest
from app.handler import handler


@pytest.fixture
def mock_dependencies(mocker):
    """
    Fixture to patch and return all external dependencies used by the handler.

    Returns:
        dict: A dictionary with all mocked dependencies.
    """
    return {
        "get_s3_object_location": mocker.patch(
            "app.handler.get_s3_object_location",
            return_value=("bucket-name", "file.json"),
        ),
        "read_json_from_s3": mocker.patch(
            "app.handler.read_json_from_s3",
            return_value={
                "interaction_id": "CHAT-001",
                "customer_id": "CUST-001",
                "transcript": "Gracias por su ayuda, excelente servicio",
            },
        ),
        "process_transcript": mocker.patch(
            "app.handler.process_transcript",
            return_value={
                "interaction_id": "CHAT-001",
                "customer_id": "CUST-001",
                "transcript": "Gracias por su ayuda, excelente servicio",
                "analysis": {"sentiment": "POSITIVE"},
            },
        ),
        "send_message_to_queue": mocker.patch(
            "app.handler.send_message_to_queue"
        ),
    }


def test_handler_success(mock_dependencies):
    """
    Test successful execution of the Lambda handler.

    Verifies that:
    - S3 object location is extracted from the event.
    - JSON is read from S3 and passed through validation/transformation.
    - Final data is sent to SQS.
    - A 200 response is returned.

    Raises:
        AssertionError: If any of the dependencies are not called as expected,
        or the response is incorrect.
    """
    mock_event = {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "bucket-name"},
                    "object": {"key": "file.json"},
                }
            }
        ]
    }

    result = handler(mock_event, context={})  # context is unused

    assert result == {"statusCode": 200, "body": "Processed successfully"}

    mock_dependencies["get_s3_object_location"].assert_called_once_with(
        mock_event
    )
    mock_dependencies["read_json_from_s3"].assert_called_once_with(
        "bucket-name", "file.json"
    )
    mock_dependencies["process_transcript"].assert_called_once()
    mock_dependencies["send_message_to_queue"].assert_called_once()
