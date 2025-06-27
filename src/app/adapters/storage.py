import os
import boto3
import json
from typing import Dict, Any
from botocore.exceptions import ClientError

s3 = boto3.client(
    "s3",
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
    endpoint_url=os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
)


def read_json_from_s3(bucket: str, key: str) -> Dict[str, Any]:
    """
    Reads and parses a JSON file from an S3 bucket.

    Args:
        bucket (str): Name of the S3 bucket.
        key (str): Key (path) to the object in the bucket.

    Returns:
        Dict[str, Any]: Parsed JSON content.

    Raises:
        ValueError: If the object is empty, not valid JSON, or not a JSON
            object.
        ClientError: If the object cannot be retrieved.
    """
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        raw_data = response["Body"].read()

        if not raw_data:
            raise ValueError(
                f"S3 object '{key}' in bucket '{bucket}' is empty"
            )

        try:
            parsed = json.loads(raw_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"S3 object '{key}' contains invalid JSON") from e

        if not isinstance(parsed, dict):
            raise ValueError(
                "Expected a JSON object, got "
                f"{type(parsed).__name__}"
            )

        return parsed

    except ClientError as e:
        raise RuntimeError(
            f"Failed to retrieve object '{key}' from bucket '{bucket}': {e}"
        ) from e
