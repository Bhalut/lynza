# ─────────────────────────────────────────────────────────────────────────────
# Lynza Makefile
# Automation for testing, building, deploying, and managing LocalStack resources
# ─────────────────────────────────────────────────────────────────────────────

.PHONY: help install format lint test test-unit test-integration coverage \
	build deploy freeze clean start-localstack stop-localstack \
	package-lambda init-localstack invoke-local trigger-s3 receive-sqs \
	run reset-local clean-lambda-artifacts

# ─────────────────────────────
# Help
# ─────────────────────────────
help:  ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-22s\033[0m %s\n", $$1, $$2}'

# ─────────────────────────────
# 📦 Installation & Environment
# ─────────────────────────────
install:  ## Install project and dev dependencies (editable mode)
	uv pip install -e .[dev]

freeze:  ## Export dependency lockfiles for reproducible builds
	uv pip freeze > requirements-dev.txt
	grep -E -v '^(awscli|awscli-local|pytest|pytest-mock|moto|coverage|black|ruff|mypy|localstack|types-boto3|types-pyyaml)' requirements-dev.txt > requirements.txt

# ─────────────────────────────
# 🧹 Code Quality
# ─────────────────────────────
format:  ## Format code using Black and Ruff
	black src tests && ruff check src tests

lint:  ## Run Ruff linter for static analysis
	ruff check src tests

# ─────────────────────────────
# Testing
# ─────────────────────────────
test:  ## Run all tests with coverage
	pytest --cov=src tests/

test-unit:  ## Run only unit tests
	pytest -m unit --cov=src tests/unit

test-integration:  ## Run only integration tests (requires LocalStack)
	pytest -m integration --cov=src tests/integration

coverage:  ## Generate HTML test coverage report
	pytest --cov=src --cov-report=html tests/

# ─────────────────────────────
# Build & Deploy
# ─────────────────────────────
build:  ## Build the SAM application
	sam build

deploy:  ## Deploy the SAM application (guided mode)
	sam deploy --guided

# ─────────────────────────────
# LocalStack (Docker) Support
# ─────────────────────────────
start-localstack:  ## Start LocalStack via docker-compose
	docker-compose up -d

stop-localstack:  ## Stop LocalStack container
	docker-compose down

reset-local: stop-localstack clean-lambda-artifacts start-localstack package-lambda init-localstack  ## Reset all local AWS resources

clean-lambda-artifacts:  ## Remove temporary Lambda build files
	rm -rf /tmp/lambda /tmp/lambda.zip

package-lambda:  ## Create zip archive for Lambda and copy it to /tmp
	mkdir -p /tmp/lambda && \
	cp -r src/app /tmp/lambda && \
	cd /tmp/lambda && zip -r /tmp/lambda.zip .

init-localstack:  ## Run resource creation script inside LocalStack container
	docker cp /tmp/lambda.zip localstack:/tmp/lambda.zip && \
	docker exec -i localstack bash /etc/localstack/init/ready.d/init_resources.sh

# ─────────────────────────────
# Manual Trigger & Debug
# ─────────────────────────────
invoke-local:  ## Invoke Lambda locally with SAM
	sam local invoke ProcessJsonFunction -e event.json

trigger-s3:  ## Upload a test file to S3 (triggers Lambda)
	awslocal s3 cp event.json s3://mi-bucket/test.json

receive-sqs:  ## Fetch a message from the SQS queue
	awslocal sqs receive-message --queue-url http://localhost:4566/000000000000/mi-cola

run:  ## Run the handler locally with mock context and S3 upload
	python3 local_runner.py

# ─────────────────────────────
# Cleanup
# ─────────────────────────────
clean:  ## Remove cache, test and build artifacts
	rm -rf .pytest_cache .mypy_cache .ruff_cache __pycache__ .coverage htmlcov .aws-sam
