# Lynza - Customer Interaction Pipeline

This project implements an AWS Lambda function that is triggered when a JSON file is uploaded to an S3 bucket. The Lambda validates and transforms the input by classifying the sentiment of a conversation, then forwards the enriched data to an SQS queue.


## Objective

Build a modular, testable, and serverless data pipeline component that:
- Reacts to events from S3
- Performs sentiment analysis
- Publishes messages to an SQS queue


## Architecture

```

S3 (upload JSON)
↓
Lambda (validation + sentiment enrichment)
↓
SQS (downstream queue)

```


## Project Structure

```

.
├── src/
│   └── app/
│       ├── handler.py                    # Lambda entrypoint
│       ├── adapters/                     # SQS/S3 abstractions
│       ├── domain/                       # Sentiment classifier
│       └── utils/                        # Event parsing helpers
├── tests/
│   ├── unit/                             # Unit tests
│   └── integration/                      # Integration with LocalStack
├── localstack/init/init\_resources.sh    # Init script for S3/SQS/Lambda
├── docker-compose.yml                    # LocalStack services
├── Makefile                              # Commands for dev & testing
├── pyproject.toml                        # Modern dependency definition
├── requirements.txt                      # Basic dependencies
├── requirements-dev.txt                  # Dev/test tools
├── README.md
└── template.yaml                         # AWS SAM infrastructure

```


## JSON Input Example

```json
{
  "interaction_id": "CHAT-123",
  "customer_id": "CUST-999",
  "transcript": "Hola, tengo un problema con mi último pedido. No ha llegado y ya pasó la fecha de entrega, necesito ayuda."
}

```

### Output Example

```json
{
  "interaction_id": "CHAT-123",
  "customer_id": "CUST-999",
  "transcript": "Hola, tengo un problema con mi último pedido. No ha llegado y ya pasó la fecha de entrega, necesito ayuda.",
  "analysis": {
    "sentiment": "NEGATIVE"
  }
}
```


## IAM Permissions Required

In a real AWS environment, this Lambda would need:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": "arn:aws:s3:::<your-bucket>/*"
    },
    {
      "Effect": "Allow",
      "Action": ["sqs:SendMessage"],
      "Resource": "arn:aws:sqs:<region>:<account-id>:<your-queue>"
    }
  ]
}
```


## Testing

### Unit Tests

```bash
make test-unit
# or manually:
pytest -m unit tests/unit
```

### Integration Tests (LocalStack)

```bash
make test-integration
# or manually:
pytest -m integration tests/integration
```

---

## Local Development Setup

### 1. Python Virtual Environment

Using `pip` and `requirements.txt`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

Or using [`uv`](https://github.com/astral-sh/uv) (faster dependency manager):

```bash
uv venv
source .venv/bin/activate
uv pip install -e .[dev]
```

---

### 2. Run the app locally

```bash
make reset-local     # Clean + package + initialize LocalStack
make run             # Execute the Lambda locally via local_runner.py
make trigger-s3      # Upload test file to S3 to simulate trigger
make receive-sqs     # Read enriched message from SQS
```


## .env File Example

```env
SQS_QUEUE_URL=http://sqs.us-east-1.localhost.localstack.cloud:4566/000000000000/mi-cola
AWS_DEFAULT_REGION=us-east-1
AWS_ENDPOINT_URL=http://localhost:4566
```


## Notes

* Sentiment detection is based on keyword matching, not ML/NLP.
* Fully modular architecture: domain, adapters, and utils are independent and testable.
* LocalStack is used to simulate AWS (S3, Lambda, SQS).
* All integration tests rely on `pytest`, `moto`, and `awslocal`.


## Author

**Abdel Mejía**
Email: [28445496+Bhalut@users.noreply.github.com](mailto:28445496+Bhalut@users.noreply.github.com)
GitHub: [@bhalut](https://github.com/bhalut)
Project: `lynza`


## 📜 License

MIT
