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

# Set bucket ACLs (development convenience) and add explicit bucket policies
echo "Setting bucket ACLs and policies..."
awslocal $AWS_REGION_OPTION s3api put-bucket-acl --bucket saeb-student-reports --acl public-read || true
awslocal $AWS_REGION_OPTION s3api put-bucket-acl --bucket saeb-report-assets --acl public-read || true
awslocal $AWS_REGION_OPTION s3api put-bucket-acl --bucket saeb-lambda-artifacts --acl public-read || true

cat >/tmp/saeb-student-reports-policy.json <<'POLICY'
{
  "Version":"2012-10-17",
  "Statement":[
    {
      "Sid":"PublicReadGetObject",
      "Effect":"Allow",
      "Principal":"*",
      "Action":["s3:GetObject"],
      "Resource":["arn:aws:s3:::saeb-student-reports/*"]
    }
  ]
}
POLICY
awslocal $AWS_REGION_OPTION s3api put-bucket-policy --bucket saeb-student-reports --policy file:///tmp/saeb-student-reports-policy.json || true
rm -f /tmp/saeb-student-reports-policy.json

cat >/tmp/saeb-report-assets-policy.json <<'POLICY'
{
  "Version":"2012-10-17",
  "Statement":[
    {
      "Sid":"PublicReadGetObject",
      "Effect":"Allow",
      "Principal":"*",
      "Action":["s3:GetObject"],
      "Resource":["arn:aws:s3:::saeb-report-assets/*"]
    }
  ]
}
POLICY
awslocal $AWS_REGION_OPTION s3api put-bucket-policy --bucket saeb-report-assets --policy file:///tmp/saeb-report-assets-policy.json || true
rm -f /tmp/saeb-report-assets-policy.json

# Allow GetObject on buckets
for bucket in \
  saeb-lambda-artifacts \
  saeb-student-reports \
  saeb-report-assets
do
  awslocal $AWS_REGION_OPTION s3api put-bucket-policy \
    --bucket "$bucket" \
    --policy "{
      \"Version\": \"2012-10-17\",
      \"Statement\": [
        {
          \"Sid\": \"PublicReadGetObject\",
          \"Effect\": \"Allow\",
          \"Principal\": \"*\",
          \"Action\": \"s3:GetObject\",
          \"Resource\": \"arn:aws:s3:::$bucket/*\"
        }
      ]
    }"
done

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
    AttributeName=filekey,AttributeType=S \
    AttributeName=createdAt,AttributeType=S \
  --key-schema \
    AttributeName=id,KeyType=HASH \
  --global-secondary-indexes '[{"IndexName":"GetByFilekey","KeySchema":[{"AttributeName":"filekey","KeyType":"HASH"},{"AttributeName":"createdAt","KeyType":"RANGE"}],"Projection":{"ProjectionType":"ALL"}}]' \
  --billing-mode PAY_PER_REQUEST

echo "DynamoDB tables created successfully!"

# Create SQS queues
echo "Creating SQS queues..."

awslocal $AWS_REGION_OPTION sqs create-queue --queue-name saeb-report-jobs-local || true

echo "SQS queues created successfully!"


