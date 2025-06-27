from typing import Dict, Any, Tuple


def get_s3_object_location(event: Dict[str, Any]) -> Tuple[str, str]:
    """
    Extracts the S3 bucket name and object key from an S3 event.

    Args:
        event (Dict[str, Any]): The AWS S3 event payload.

    Returns:
        Tuple[str, str]: The bucket name and object key.

    Raises:
        KeyError: If the event structure is missing expected fields.
        IndexError: If no records are present in the event.

    Example:
        >>> get_s3_object_location({
        ...     "Records": [{
        ...         "s3": {
        ...             "bucket": {"name": "example-bucket"},
        ...             "object": {"key": "folder/data.json"}
        ...         }
        ...     }]
        ... })
        ('example-bucket', 'folder/data.json')
    """
    try:
        record = event["Records"][0]
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]
        return bucket, key

    except (IndexError, KeyError, TypeError) as e:
        raise KeyError("Invalid S3 event structure") from e
