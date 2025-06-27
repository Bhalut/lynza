#!/bin/bash
# ------------------------------------------------------------------------------
# init_resources.sh
#
# Initializes AWS resources in LocalStack: S3 bucket, SQS queue, and Lambda function.
# Also configures S3 to trigger the Lambda on object creation.
#
# Usage:
#   docker exec -i localstack bash /etc/localstack/init/ready.d/init_resources.sh
#
# Dependencies:
#   - awslocal (installed in the LocalStack container)
#   - Lambda zip must be located at /tmp/lambda.zip inside container
# ------------------------------------------------------------------------------

set -e

echo "🔧 Initializing AWS resources in LocalStack..."

# ----------------------------
# S3 Bucket
# ----------------------------
echo "📦 Creating S3 bucket: mi-bucket"
awslocal s3 mb s3://mi-bucket || echo "📦 Bucket already exists"

# ----------------------------
# SQS Queue
# ----------------------------
echo "📨 Creating SQS queue: mi-cola"
QUEUE_URL=$(awslocal sqs create-queue \
  --queue-name mi-cola \
  --query 'QueueUrl' \
  --output text)
echo "🔗 SQS_QUEUE_URL=$QUEUE_URL"

# ----------------------------
# Lambda Function
# ----------------------------
echo "⚙️ Checking if Lambda function exists: procesar-json"
if awslocal lambda get-function --function-name procesar-json &>/dev/null; then
  echo "⚠️ Lambda already exists. Deleting..."
  awslocal lambda delete-function --function-name procesar-json
  sleep 2
fi

echo "⚙️ Creating Lambda function: procesar-json"
awslocal lambda create-function \
  --function-name procesar-json \
  --runtime python3.8 \
  --handler lambda_function.lambda_handler \
  --role arn:aws:iam::000000000000:role/lambda-role \
  --zip-file fileb:///tmp/lambda.zip

# ----------------------------
# Wait for Lambda readiness
# ----------------------------
echo "⏳ Waiting for Lambda to become active..."
while true; do
  STATUS=$(awslocal lambda get-function-configuration \
    --function-name procesar-json \
    --query 'State' \
    --output text)
  if [ "$STATUS" = "Active" ]; then
    break
  fi
  echo "⏳ Current status: $STATUS. Waiting..."
  sleep 1
done

# ----------------------------
# S3 Notification → Lambda
# ----------------------------
echo "🔗 Configuring S3 notification to trigger Lambda on object creation"
awslocal s3api put-bucket-notification-configuration --bucket mi-bucket --notification-configuration '{
  "LambdaFunctionConfigurations": [
    {
      "LambdaFunctionArn": "arn:aws:lambda:us-east-1:000000000000:function:procesar-json",
      "Events": ["s3:ObjectCreated:*"]
    }
  ]
}'

# ----------------------------
# Summary
# ----------------------------
echo ""
echo "✅ All resources have been initialized successfully."
echo "🔗 Add this to your .env if missing:"
echo "SQS_QUEUE_URL=$QUEUE_URL"
