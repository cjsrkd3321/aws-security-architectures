resource "aws_secretsmanager_secret" "this" {
  name_prefix = "event-alarm-secret"
}

resource "aws_secretsmanager_secret_policy" "this" {
  secret_arn = aws_secretsmanager_secret.this.arn

  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "GetValueForSpecificRole",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "secretsmanager:GetSecretValue",
      "Resource": "*",
      "Condition": {
        "ArnNotEquals": {
            "aws:PrincipalArn": "${module.lambda_function.lambda_role_arn}"
        }
      }
    }
  ]
}
POLICY
}

resource "aws_secretsmanager_secret_version" "this" {
  secret_id = aws_secretsmanager_secret.this.id
  secret_string = jsonencode({
    slack_webhook_url = var.slack_webhook_url
    slack_channel     = var.channel
  })
}