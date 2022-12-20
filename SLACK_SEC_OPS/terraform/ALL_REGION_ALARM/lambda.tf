module "lambda_function" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "security-alarm-lambda"
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.9"

  source_path = "func"

  timeout     = 60
  memory_size = 512

  cloudwatch_logs_retention_in_days = 1

  attach_policy_json = true
  policy_json        = <<-EOT
      {
          "Version": "2012-10-17",
          "Statement": [
              {
                  "Effect": "Allow",
                  "Action": [
                      "secretsmanager:GetSecretValue"
                  ],
                  "Resource": ["${aws_secretsmanager_secret.this.arn}"]
              }
          ]
      }
    EOT

  environment_variables = {
    SECRET_ARN      = aws_secretsmanager_secret.this.arn
    SOURCE_IPS      = jsonencode(concat(var.my_ips, ["AWS Internal"]))
    SENSITIVE_PORTS = jsonencode([22, 3389])
    ALLOWED_IPS     = jsonencode(["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"])
  }
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  for_each = aws_cloudwatch_event_rule.use1

  action        = "lambda:InvokeFunction"
  function_name = module.lambda_function.lambda_function_name
  principal     = "events.amazonaws.com"
  source_arn    = each.value.arn
}