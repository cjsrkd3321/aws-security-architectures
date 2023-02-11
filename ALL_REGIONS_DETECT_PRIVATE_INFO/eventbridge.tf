resource "aws_cloudwatch_event_rule" "use1" {
  name = "macie-inspect-rule"
  #   schedule_expression = "rate(25 minutes)"
  schedule_expression = "cron(30 10 * * ? *)"
}

resource "aws_cloudwatch_event_target" "default_use1" {
  rule = aws_cloudwatch_event_rule.use1.name
  arn  = module.lambda_function.lambda_function_arn
}

# https://acloudguru.com/blog/engineering/how-to-keep-your-lambda-functions-warm
resource "aws_cloudwatch_event_rule" "use1_warm" {
  name                = "macie-lambda-warming-rule"
  schedule_expression = "rate(5 minutes)"
}

resource "aws_cloudwatch_event_target" "default_warn_use1" {
  rule = aws_cloudwatch_event_rule.use1_warm.name
  arn  = module.lambda_function.lambda_function_arn
  input = jsonencode(
    {
      "warmer" = true
    }
  )
}