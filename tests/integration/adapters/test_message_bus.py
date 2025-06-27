import json
import boto3
import pytest
from app.adapters.message_bus import send_message_to_queue


@pytest.mark.integration
def test_send_message_to_sqs_localstack(setup_sqs_queue):
    """
    Integration test for sending a message to SQS via LocalStack.

    Publishes a message to the configured queue and confirms
    that it can be received from the queue.

    Args:
        setup_sqs_queue (str): The URL of the SQS queue from a fixture.

    Raises:
        AssertionError: If the message is not received or malformed.
    """
    message = {"interaction_id": "CHAT-123", "sentiment": "POSITIVE"}

    send_message_to_queue(message)

    sqs = boto3.client("sqs", endpoint_url="http://localhost:4566")
    response = sqs.receive_message(QueueUrl=setup_sqs_queue)

    assert "Messages" in response
    body = json.loads(response["Messages"][0]["Body"])
    assert body == message
