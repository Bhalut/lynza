import boto3
import json
import os
from typing import Dict
from botocore.exceptions import ClientError, ParamValidationError

sqs = boto3.client(
    "sqs",
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
    endpoint_url=os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
)


def send_message_to_queue(payload: Dict) -> None:
    """
    Publishes a JSON message to an AWS SQS queue.

    Args:
        payload (Dict): The message payload to be serialized and sent.

    Raises:
        ValueError: If the payload could not be serialized or sent.
    """
    queue_url = os.getenv("SQS_QUEUE_URL")
    if not queue_url:
        raise RuntimeError("Missing environment variable: SQS_QUEUE_URL")

    try:
        message_body = json.dumps(payload)

        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=message_body
        )
    except (ClientError, ParamValidationError, TypeError) as e:
        raise ValueError(f"Failed to send message to SQS: {e}") from e
