resource "aws_cloudwatch_event_rule" "this" {
  name        = "rolesanywhere-expiration-event-rule"
  description = "rolesanywhere-expiration-event-rule"

  event_pattern = <<EOF
{
  "source": ["aws.rolesanywhere"],
  "detail-type": [{
    "prefix": "Roles Anywhere"
  }]
}
EOF
}

resource "aws_cloudwatch_event_target" "sns" {
  rule = aws_cloudwatch_event_rule.this.name
  arn  = aws_sns_topic.this.arn
}