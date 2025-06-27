from typing import Dict, Any

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

from app.adapters.storage import read_json_from_s3
from app.adapters.message_bus import send_message_to_queue
from app.utils.parse_event import get_s3_object_location
from app.domain.sentiment_analysis import process_transcript
from dotenv import load_dotenv

load_dotenv()


logger = Logger(service="lynza")


@logger.inject_lambda_context(log_event=True)
def handler(
    event: Dict[str, Any],
    context: LambdaContext
) -> Dict[str, Any]:
    """
    Lambda entrypoint triggered by S3 upload events.

    This function is triggered whenever a JSON file is uploaded to a specific
    S3 bucket. It extracts the file location, retrieves the JSON content,
    validates and transforms the payload, and sends the resulting message to an
    SQS queue.

    Args:
        event (Dict[str, Any]): The S3 event payload.
        context (LambdaContext): Lambda execution context.

    Returns:
        Dict[str, Any]: Status response for observability or future
            integration.

    Raises:
        ValueError: If the JSON file content is invalid.
        Exception: If any other unexpected error occurs.
    """
    try:
        bucket, key = get_s3_object_location(event)
        logger.info("S3 event received", extra={"bucket": bucket, "key": key})

        json_data = read_json_from_s3(bucket, key)
        logger.debug("Raw JSON data retrieved", extra={"data": json_data})

        transformed_data = process_transcript(json_data)
        logger.debug(
            "Transformed data",
            extra={"transformed": transformed_data}
        )

        send_message_to_queue(transformed_data)
        logger.info("Message successfully sent to SQS")

        return {"statusCode": 200, "body": "Processed successfully"}

    except KeyError as e:
        logger.error(
            "Malformed S3 event payload",
            extra={"error": str(e)},
            exc_info=True
        )
        raise

    except ValueError as validation_error:
        logger.error(
            "Validation failed",
            extra={"error": str(validation_error)},
            exc_info=True
        )
        raise

    except Exception as e:
        logger.exception(
            "Unexpected error during processing",
            extra={"error": str(e)}
        )
        raise
