provider "aws" {
  region = "ap-northeast-2"
  default_tags {
    tags = {
      Owner = "rex.chun"
    }
  }
}

### VARIABLES ###
variable "email" {
  type = string
}

### LAMBDA ###
module "lambda_function" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "nuke-lambda-function"
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.8"
  source_path   = "func"
  timeout       = 900
  memory_size   = 2048

  publish = true
  # allowed_triggers = {
  #   EventBridge = {
  #     principal  = "events.amazonaws.com"
  #     source_arn = aws_cloudwatch_event_rule.eventbridge_rule.arn
  #   }
  # }

  environment_variables = {
    IS_RUN_DELETE   = "TRUE" # "TRUE" or "FALSE"
    MAX_WORKERS     = 500
    MAX_SLEEP       = 15
    MAX_RUNNING_TIME = 850
    MAX_ITER_COUNTS = 50
    TOPIC_ARN       = aws_sns_topic.this.arn
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

### SNS ###
resource "aws_sns_topic" "this" {
  name = "nuke-sns-topic"
}

resource "aws_sns_topic_subscription" "this" {
  topic_arn = aws_sns_topic.this.arn
  protocol  = "email"
  endpoint  = var.email
}