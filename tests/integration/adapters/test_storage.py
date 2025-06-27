import json
import boto3
import pytest
from app.adapters.storage import read_json_from_s3


@pytest.mark.integration
def test_read_json_from_s3_integration(setup_s3_bucket):
    """
    Tests the retrieval and parsing of a JSON file from S3 using LocalStack.

    This test uploads a JSON file to a mock S3 bucket hosted by LocalStack,
    then verifies that the `read_json_from_s3` function correctly fetches
    and parses the content into a Python dictionary.

    Args:
        setup_s3_bucket (str): Name of the test S3 bucket, created via fixture.

    Raises:
        AssertionError: If the parsed content does not match the expected
            payload.
    """
    s3 = boto3.client("s3", endpoint_url="http://localhost:4566")
    bucket = setup_s3_bucket
    key = "test.json"
    payload = {"hello": "world"}

    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(payload),
        ContentType="application/json"
    )

    result = read_json_from_s3(bucket, key)

    assert result == payload
