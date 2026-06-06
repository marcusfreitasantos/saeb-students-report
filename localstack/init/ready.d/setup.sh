#!/bin/sh
set -e

export AWS_REGION="${AWS_REGION:-sa-east-1}"
export AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION:-sa-east-1}"

AWS_REGION_OPTION="--region ${AWS_REGION}"

# Helper para criação idempotente de tabelas
create_table_if_not_exists() {
  table_name="$1"
  shift

  if awslocal $AWS_REGION_OPTION dynamodb describe-table --table-name "$table_name" >/dev/null 2>&1; then
    echo "Table $table_name already exists, skipping."
    return 0
  fi

  echo "Creating DynamoDB table: $table_name"
  awslocal $AWS_REGION_OPTION dynamodb create-table "$@"
}

# Create S3 buckets
awslocal $AWS_REGION_OPTION s3 mb "s3://saeb-lambda-artifacts" || true
awslocal $AWS_REGION_OPTION s3 mb "s3://saeb-student-reports" || true
awslocal $AWS_REGION_OPTION s3 mb "s3://saeb-report-assets" || true

# Create DynamoDB tables
echo "Creating DynamoDB tables..."

create_table_if_not_exists saeb_questions_local \
  --table-name saeb_questions_local \
  --attribute-definitions AttributeName=id,AttributeType=S \
  --key-schema AttributeName=id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

create_table_if_not_exists saeb_interventions_local \
  --table-name saeb_interventions_local \
  --attribute-definitions \
    AttributeName=id,AttributeType=S \
    AttributeName=category,AttributeType=S \
    AttributeName=descriptor,AttributeType=S \
  --key-schema \
    AttributeName=id,KeyType=HASH \
    AttributeName=category,KeyType=RANGE \
  --global-secondary-indexes '[{"IndexName":"GetByCategoryAndDescriptor","KeySchema":[{"AttributeName":"category","KeyType":"HASH"},{"AttributeName":"descriptor","KeyType":"RANGE"}],"Projection":{"ProjectionType":"ALL"}}]' \
  --billing-mode PAY_PER_REQUEST

create_table_if_not_exists saeb_reports_local \
  --table-name saeb_reports_local \
  --attribute-definitions \
    AttributeName=id,AttributeType=S \
  --key-schema \
    AttributeName=id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

echo "DynamoDB tables created successfully!"
