# EVENTSRules
resource "aws_cloudwatch_event_rule" "this" {
  name        = "capture-aws-sign-in"
  description = "Capture each AWS Console Sign In"

  event_pattern = <<EOF
{
  "detail-type": [
    "AWS Console Sign In via CloudTrail"
  ]
}
EOF
}

# EVENTSRules
resource "aws_cloudwatch_event_target" "this" {
  rule      = aws_cloudwatch_event_rule.this.name
  target_id = "SendToSNS"
  arn       = aws_sns_topic.aws_logins.arn
}

# EVENTSBuses
resource "aws_cloudwatch_event_bus" "this" {
  name = "nuke-event-bus"
}
