import json
from io import BytesIO
import pytest
from botocore.exceptions import ClientError
from app.adapters.storage import read_json_from_s3


@pytest.fixture
def mock_s3(mocker):
    """
    Mocks the S3 client used inside the storage module.

    Returns:
        Mock: A patched version of boto3 S3 client.
    """
    return mocker.patch("app.adapters.storage.s3")


def test_read_json_success(mock_s3):
    """
    Should return the parsed JSON when a valid JSON object is retrieved
    from S3.

    Mocks the S3 get_object response to return a valid JSON body and asserts
    that the function returns the expected dictionary.

    Args:
        mock_s3 (Mock): Mocked S3 client.
    """
    expected = {"key": "value"}
    mock_s3.get_object.return_value = {
        "Body": BytesIO(json.dumps(expected).encode())
    }

    result = read_json_from_s3("my-bucket", "data.json")

    assert result == expected
    mock_s3.get_object.assert_called_once_with(
        Bucket="my-bucket", Key="data.json"
    )


def test_read_json_empty_object(mock_s3):
    """
    Should raise ValueError when the S3 object is empty.

    Simulates an empty file in S3 and ensures the function raises an
    appropriate error.

    Args:
        mock_s3 (Mock): Mocked S3 client.
    """
    mock_s3.get_object.return_value = {"Body": BytesIO(b"")}

    with pytest.raises(ValueError, match="is empty"):
        read_json_from_s3("my-bucket", "data.json")


def test_read_json_invalid_json(mock_s3):
    """
    Should raise ValueError when the S3 object contains malformed JSON.

    Ensures that invalid JSON content is caught and converted to a ValueError.

    Args:
        mock_s3 (Mock): Mocked S3 client.
    """
    mock_s3.get_object.return_value = {"Body": BytesIO(b"{invalid json}")}

    with pytest.raises(ValueError, match="contains invalid JSON"):
        read_json_from_s3("my-bucket", "data.json")


def test_read_json_not_a_dict(mock_s3):
    """
    Should raise ValueError when the JSON content is not a dictionary.

    Verifies that the function rejects valid JSON that is not a JSON object.

    Args:
        mock_s3 (Mock): Mocked S3 client.
    """
    mock_s3.get_object.return_value = {
        "Body": BytesIO(json.dumps(["list", "not", "dict"]).encode())
    }

    with pytest.raises(ValueError, match="Expected a JSON object"):
        read_json_from_s3("my-bucket", "data.json")


def test_read_json_s3_client_error(mock_s3):
    """
    Should raise ClientError when S3 fails to retrieve the object.

    Mocks a ClientError from boto3 and asserts it is propagated by the
    function.

    Args:
        mock_s3 (Mock): Mocked S3 client.
    """
    mock_s3.get_object.side_effect = ClientError(
        {
            "Error": {
                "Code": "NoSuchKey",
                "Message": "Object not found"
            }
        },
        "GetObject"
    )

    with pytest.raises(ClientError, match="Failed to retrieve object"):
        read_json_from_s3("my-bucket", "missing.json")
