resource "aws_cloudwatch_event_rule" "use1" {
  name = "macie-inspect-rule"
  #   schedule_expression = "rate(25 minutes)"
  schedule_expression = "cron(30 * * * ? *)"
}

resource "aws_cloudwatch_event_target" "default_use1" {
  rule = aws_cloudwatch_event_rule.use1.name
  arn  = module.lambda_function.lambda_function_arn
}