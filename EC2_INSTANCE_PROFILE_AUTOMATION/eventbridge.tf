resource "aws_cloudwatch_event_rule" "eventbridge_rule" {
  name        = "ec2-instance-profile-automation-event-bridge-rule"
  description = "EC2 INSTANCE PROFILE AUTOMATION"

  schedule_expression = "rate(1 hour)"
}

resource "aws_cloudwatch_event_target" "lambda" {
  rule = aws_cloudwatch_event_rule.eventbridge_rule.name
  arn  = module.lambda_function.lambda_function_arn
}