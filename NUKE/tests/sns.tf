# SNSTopics
resource "aws_sns_topic" "this" {
  name = "nuke-topic"
}

# SNSTopics
resource "aws_sns_topic" "aws_logins" {
  name = "nuke-aws-console-logins"
}

# SNSTopics
resource "aws_sns_topic_policy" "this" {
  arn    = aws_sns_topic.aws_logins.arn
  policy = data.aws_iam_policy_document.sns_topic_policy.json
}
