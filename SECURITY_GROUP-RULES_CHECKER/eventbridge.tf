resource "aws_cloudwatch_event_rule" "this" {
  name                = var.scheduled_rule_name
  schedule_expression = "cron(0 01 * * ? *)"
}

resource "aws_cloudwatch_event_target" "this" {
  rule = aws_cloudwatch_event_rule.this.name
  arn  = module.lambda_function.lambda_function_arn
}