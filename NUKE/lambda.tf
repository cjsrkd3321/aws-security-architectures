provider "aws" {
  region = "ap-northeast-2"
  default_tags {
    tags = {
      Owner = "rex.chun"
    }
  }
}

module "lambda_function" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "aws-nuke-lambda"
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.8"
  source_path   = "func"
  timeout       = 240
  memory_size   = 2048
  publish       = true
  # allowed_triggers = {
  #   EventBridge = {
  #     principal  = "events.amazonaws.com"
  #     source_arn = aws_cloudwatch_event_rule.eventbridge_rule.arn
  #   }
  # }
  environment_variables = {
    IS_RUN_DELETE   = "FALSE"
    MAX_WORKERS     = 25
    MAX_SLEEP       = 10
    MAX_ITER_COUNTS = 60
  }
  attach_policy = true
  policy        = "arn:aws:iam::aws:policy/AdministratorAccess"
  layers = [
    aws_lambda_layer_version.this.arn
  ]
}

resource "aws_lambda_layer_version" "this" {
  filename            = "python.zip"
  layer_name          = "nuke-layer"
  compatible_runtimes = ["python3.8"]
}