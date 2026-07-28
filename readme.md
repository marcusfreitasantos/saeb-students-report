# SAEB Backend Local Development

## Prerequisites

- Docker
- Docker Compose
- AWS SAM CLI
- Python 3.12 (for SAM local execution)
- `awslocal` if you want to interact with LocalStack from the host, otherwise use `docker compose exec`

## Start LocalStack

From the project root:

```bash
cd /Users/marcusfreitas/Projetos/S/saeb/backend
docker compose up -d --build
```

LocalStack will start on port `4566` and run the configured services:

- S3
- DynamoDB
- SQS
- Lambda
- API Gateway
- CloudWatch
- IAM

The initialization script `localstack/init/ready.d/setup.sh` creates S3 buckets, DynamoDB tables, and the SQS queue used by this project.

## Invoke Lambdas with Event Files

Each function folder contains a SAM template and can be invoked locally with `sam local invoke`.

### Generate Presigned URL

```bash
cd /Users/marcusfreitas/Projetos/S/saeb/backend/src/functions/generate-presigned-url
sam local invoke GeneratePresignedUrlFunction -e ../../../../src/events/http-event.json
```

### Generate Report

```bash
cd /Users/marcusfreitas/Projetos/S/saeb/backend/src/functions/generate-report
sam local invoke GenerateReportFunction -e ../../../../src/events/sqs-event.json
```

### Manage Report Questions

```bash
cd /Users/marcusfreitas/Projetos/S/saeb/backend/src/functions/manage-report-questions
sam local invoke ManageReportQuestionsFunction -e ../../../../src/functions/manage-report-questions/events/event.json
```

## Start SAM Local API

You can start a local API for each SAM template using `sam local start-api`.

### Generate Presigned URL API

```bash
cd /Users/marcusfreitas/Projetos/S/saeb/backend/src/functions/generate-presigned-url
sam local start-api --template template.yml --port 3001
```

Then invoke the endpoint in another shell:

```bash
curl -X POST http://127.0.0.1:3001/report/generate-url
```

### Generate Report API

```bash
cd /Users/marcusfreitas/Projetos/S/saeb/backend/src/functions/generate-report
sam local start-api --template template.yml --port 3002
```

Then invoke the endpoint:

```bash
curl http://127.0.0.1:3002/report/{key}
```

### Manage Report Questions API

```bash
cd /Users/marcusfreitas/Projetos/S/saeb/backend/src/functions/manage-report-questions
sam local start-api --template template.yml --port 3003
```

Then invoke endpoints such as:

```bash
curl http://127.0.0.1:3003/questions/all
curl -X POST http://127.0.0.1:3003/questions/create -H "Content-Type: application/json" -d @events/event.json
```

## Notes

- The LocalStack environment is configured through `docker-compose.yml` and the initialization script in `localstack/init/ready.d/setup.sh`.
- The functions use LocalStack endpoints via environment variables, such as `http://host.docker.internal:4566`.
- If you change the port for LocalStack, update both `docker-compose.yml` and the function environment setup.
