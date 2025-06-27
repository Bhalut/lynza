import json
import boto3
import pytest
from app.handler import handler


@pytest.mark.integration
def test_handler_end_to_end_with_localstack(setup_s3_bucket, setup_sqs_queue):
    """
    Integration test for the full Lambda handler flow using LocalStack.

    This test uploads a JSON file to a mocked S3 bucket, invokes the handler
    with a simulated S3 event, and verifies that the expected message is
    sent to SQS after processing the transcript.

    Args:
        setup_s3_bucket (str): Name of the test S3 bucket, provided by fixture.
        setup_sqs_queue (str): URL of the test SQS queue, provided by fixture.

    Raises:
        AssertionError: If the message is not sent or its structure is
            incorrect.
    """
    s3 = boto3.client("s3", endpoint_url="http://localhost:4566")
    sqs = boto3.client("sqs", endpoint_url="http://localhost:4566")

    key = "sample-transcript.json"
    input_payload = {
        "interaction_id": "CHAT-9000",
        "customer_id": "CUST-9000",
        "transcript": (
            "Hola, tengo un problema con mi pedido y necesito ayuda urgente"
        ),
    }

    s3.put_object(
        Bucket=setup_s3_bucket,
        Key=key,
        Body=json.dumps(input_payload),
        ContentType="application/json",
    )

    event = {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": setup_s3_bucket},
                    "object": {"key": key},
                }
            }
        ]
    }

    response = handler(event, context={})

    assert response["statusCode"] == 200
    assert response["body"] == "Processed successfully"

    sqs_response = sqs.receive_message(
        QueueUrl=setup_sqs_queue, MaxNumberOfMessages=1, WaitTimeSeconds=2
    )

    assert "Messages" in sqs_response
    message = json.loads(sqs_response["Messages"][0]["Body"])

    assert message["interaction_id"] == input_payload["interaction_id"]
    assert message["customer_id"] == input_payload["customer_id"]
    assert message["transcript"] == input_payload["transcript"]
    assert message["analysis"]["sentiment"] == "NEGATIVE"
