import json
import time
import boto3
from pathlib import Path
from botocore.exceptions import ClientError
from src.app.handler import handler


# Configuration
BUCKET_NAME = "mi-bucket"
OBJECT_KEY = "test.json"
EVENT_PATH = Path("event.json")
PAYLOAD_PATH = Path("sample_payload.json")


class MockLambdaContext:
    """Mocked AWS Lambda context object for local testing.

    Attributes:
        function_name (str): Name of the Lambda function.
        function_version (str): Version identifier for the Lambda function.
        invoked_function_arn (str): ARN of the invoked Lambda function.
        memory_limit_in_mb (int): Memory limit configured for the function.
        aws_request_id (str): Simulated AWS request ID.
        log_group_name (str): CloudWatch log group name.
        log_stream_name (str): CloudWatch log stream name.
        identity: Placeholder for identity context (None).
        client_context: Placeholder for client context (None).
    """

    function_name = "lynza-local"
    function_version = "$LATEST"
    invoked_function_arn = (
        "arn:aws:lambda:us-east-1:000000000000:function:lynza"
    )
    memory_limit_in_mb = 128
    aws_request_id = "test-invoke-123"
    log_group_name = "/aws/lambda/lynza"
    log_stream_name = "2024/06/27/[$LATEST]abcdef1234567890"
    identity = None
    client_context = None


def upload_sample_to_s3():
    """Uploads a sample JSON file to a local S3 bucket using LocalStack.

    If the bucket does not exist, it will be created. The sample file is read
    from the path defined in PAYLOAD_PATH and uploaded under OBJECT_KEY.

    Raises:
        botocore.exceptions.ClientError: If any AWS-related error occurs.
    """
    s3 = boto3.client(
        "s3",
        endpoint_url="http://localhost:4566",
        region_name="us-east-1"
    )

    try:
        s3.head_bucket(Bucket=BUCKET_NAME)
    except ClientError:
        s3.create_bucket(Bucket=BUCKET_NAME)

    with open(PAYLOAD_PATH, "rb") as f:
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=OBJECT_KEY,
            Body=f,
            ContentType="application/json"
        )

    time.sleep(1)  # Ensure the object is available for eventual consistency


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    upload_sample_to_s3()

    with open(EVENT_PATH) as f:
        event = json.load(f)

    result = handler(event, MockLambdaContext())
    print("✅ Handler result:", result)
