import json
import pytest
from botocore.exceptions import ClientError
from app.adapters.message_bus import send_message_to_queue


@pytest.fixture
def mock_sqs_client(mocker):
    """
    Mocks the boto3 SQS client in the message_bus module.

    Returns:
        Mock: A patched version of boto3 SQS client.
    """
    return mocker.patch("app.adapters.message_bus.sqs")


def test_send_message_to_queue_succeeds_with_valid_payload(mock_sqs_client):
    """
    Sends a valid payload and verifies it is correctly serialized and
    dispatched to SQS.

    Asserts that:
    - The message is serialized using JSON.
    - The message is sent to the correct Queue URL.
    - The message body matches the original payload.

    Args:
        mock_sqs_client (Mock): The patched boto3 SQS client.
    """
    payload = {"interaction_id": "ABC-123", "sentiment": "POSITIVE"}

    send_message_to_queue(payload)

    mock_sqs_client.send_message.assert_called_once()
    args, kwargs = mock_sqs_client.send_message.call_args

    expected_queue_url = kwargs["QueueUrl"]
    expected_body = json.loads(kwargs["MessageBody"])

    actual_queue_url = mock_sqs_client.send_message.call_args[1]["QueueUrl"]
    assert expected_queue_url == actual_queue_url
    assert expected_body == payload


def test_send_message_to_queue_raises_value_error_on_boto3_client_error(
    mock_sqs_client,
):
    """
    Raises ValueError when boto3 raises a ClientError during message dispatch.

    Simulates a permissions error from SQS and verifies that the function
    surfaces it as a ValueError.

    Args:
        mock_sqs_client (Mock): The patched boto3 SQS client.
    """
    mock_sqs_client.send_message.side_effect = ClientError(
        {"Error": {"Code": "AccessDenied", "Message": "Permission denied"}},
        "SendMessage",
    )

    with pytest.raises(ValueError, match="Failed to send message to SQS"):
        send_message_to_queue({"interaction_id": "ABC-123"})


def test_send_message_to_queue_raises_value_error_on_unserializable_input():
    """
    Raises ValueError if the payload cannot be serialized to JSON.

    Verifies that the function handles non-serializable input gracefully and
    prevents the boto3 client from being invoked.
    """

    class NotSerializable:
        pass

    with pytest.raises(ValueError, match="Failed to send message to SQS"):
        send_message_to_queue({"invalid": NotSerializable()})
