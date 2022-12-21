module "lambda_function" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "my-lambda1"
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.9"
  publish       = true

  source_path = "func"

  timeout     = 60
  memory_size = 1024

  cloudwatch_logs_retention_in_days = 1

  environment_variables = {
    SECRET_ARN      = aws_secretsmanager_secret.this.arn
    DENY_POLICY_ARN = aws_iam_policy.this.arn
    MANAGER         = var.manager
  }

  allowed_triggers = {
    APIGatewaySlack = {
      service    = "apigateway"
      source_arn = "${aws_apigatewayv2_api.this.execution_arn}/*/*/${var.path}"
    },
  }

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
              },
              {
                  "Effect": "Allow",
                  "Action": [
                      "iam:Attach*",
                      "iam:Detach*",
                      "iam:DeleteAccessKey",
                      "cloudtrail:LookupEvents",
                      "ec2:DescribeRegions"
                  ],
                  "Resource": ["*"]
              }
          ]
      }
    EOT

  layers = [
    aws_lambda_layer_version.this.arn
  ]
}

resource "aws_lambda_layer_version" "this" {
  filename            = "python.zip"
  layer_name          = "apigw-slack-layer"
  compatible_runtimes = ["python3.9"]
}