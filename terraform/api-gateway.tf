resource "aws_apigatewayv2_api" "saeb_api" {
  name          = "saeb-students-report-api"
  protocol_type = "HTTP"

  tags = local.common_tags

}

resource "aws_apigatewayv2_integration" "lambda" {
  api_id = aws_apigatewayv2_api.saeb_api.id

  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.manage_report_questions.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "create_question" {
  api_id = aws_apigatewayv2_api.saeb_api.id

  route_key = "POST /questions/create"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_route" "create_intervention" {
  api_id = aws_apigatewayv2_api.saeb_api.id

  route_key = "POST /interventions/create"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"

  function_name = aws_lambda_function.manage_report_questions.function_name

  principal = "apigateway.amazonaws.com"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id = aws_apigatewayv2_api.saeb_api.id

  name        = "$default"
  auto_deploy = true
}

output "api_url" {
  value = aws_apigatewayv2_api.saeb_api.api_endpoint
}