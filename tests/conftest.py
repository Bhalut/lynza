import os
import boto3
import pytest


@pytest.fixture(scope="module")
def s3_resource():
    """
    Provides a boto3 S3 resource configured for LocalStack.

    Returns:
        boto3.resources.factory.s3.ServiceResource: A boto3 S3 resource object.
    """
    return boto3.resource("s3", endpoint_url="http://localhost:4566")


@pytest.fixture
def setup_s3_bucket(s3_resource):
    """
    Creates a temporary S3 bucket in LocalStack for testing.

    Returns:
        str: The name of the created bucket.
    """
    bucket_name = "test-bucket"
    s3_resource.create_bucket(Bucket=bucket_name)
    return bucket_name


@pytest.fixture(scope="module")
def setup_sqs_queue():
    """
    Creates an SQS queue in LocalStack for integration testing and
    sets env var.

    Returns:
        str: The queue URL.
    """
    queue_name = "test-queue"
    sqs = boto3.client("sqs", endpoint_url="http://localhost:4566")
    response = sqs.create_queue(QueueName=queue_name)

    # Set environment variable for application use
    os.environ["SQS_QUEUE_URL"] = response["QueueUrl"]

    return response["QueueUrl"]


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    """
    Automatically ensures SQS_QUEUE_URL is reset before each test.

    Prevents leak of environment state between tests.
    """
    monkeypatch.delenv("SQS_QUEUE_URL", raising=False)
