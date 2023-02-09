resource "aws_sns_topic" "this" {
  name         = "rolesanywhere-expiration-topic"
  display_name = "rolesanywhere-expiration-topic"
}

resource "aws_sns_topic_subscription" "this" {
  topic_arn = aws_sns_topic.this.arn
  protocol  = "email"
  endpoint  = var.endpoint_mail
}