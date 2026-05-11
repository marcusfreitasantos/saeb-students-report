resource "aws_lambda_function" "manage_report_questions" {
  function_name = "manage-report-questions"

  filename         = "default-lambda.zip"
  source_code_hash = filebase64sha256("default-lambda.zip")

  role = aws_iam_role.saeb_lambda_role.arn

  handler = "main.handler"
  runtime = "python3.12"
  timeout = 30

  environment {
    variables = {
      DYNAMO_QUESTIONS_TABLE = var.DYNAMO_QUESTIONS_TABLE
      DYNAMMO_INTERVENTIONS_TABLE = var.DYNAMMO_INTERVENTIONS_TABLE
    }
  }

  tags = local.common_tags
}