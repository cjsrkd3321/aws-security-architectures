resource "aws_apigatewayv2_api" "this" {
  name          = "slacktest"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "this" {
  api_id                 = aws_apigatewayv2_api.this.id
  integration_type       = "AWS_PROXY"
  payload_format_version = "2.0" # https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-lambda.html#http-api-develop-integrations-lambda.proxy-format
  integration_uri        = module.lambda_function.lambda_function_arn
}

resource "aws_apigatewayv2_route" "this" {
  api_id    = aws_apigatewayv2_api.this.id
  route_key = "POST /rextest"
  target    = "integrations/${aws_apigatewayv2_integration.this.id}"
}

resource "aws_apigatewayv2_stage" "this" {
  api_id      = aws_apigatewayv2_api.this.id
  name        = "$default"
  auto_deploy = true
  default_route_settings {
    throttling_burst_limit = 100 # Maximum 5,000
    throttling_rate_limit  = 100 # Maximum 10,000
  }
}

output "api_endpoint" {
  value = join("", [aws_apigatewayv2_stage.this.invoke_url, split("/", aws_apigatewayv2_route.this.route_key)[1]])
}