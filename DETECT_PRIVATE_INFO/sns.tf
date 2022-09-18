# https://docs.aws.amazon.com/ko_kr/systems-manager/latest/userguide/monitoring-sns-examples.html
resource "aws_sns_topic" "ssm_topic" {
  name = var.topic_name
}

resource "aws_sns_topic_subscription" "user_updates_sqs_target" {
  topic_arn = aws_sns_topic.ssm_topic.arn
  protocol  = "lambda"
  endpoint  = module.lambda_function.lambda_function_arn
}

# apne2
resource "aws_sns_topic" "ssm_topic_apne2" {
  provider = aws.apne2
  name     = var.topic_name
}

resource "aws_sns_topic_subscription" "user_updates_sqs_target_apne2" {
  provider = aws.apne2

  topic_arn = aws_sns_topic.ssm_topic_apne2.arn
  protocol  = "lambda"
  endpoint  = module.lambda_function.lambda_function_arn
}

# apne1
resource "aws_sns_topic" "ssm_topic_apne1" {
  provider = aws.apne1
  name     = var.topic_name
}

resource "aws_sns_topic_subscription" "user_updates_sqs_target_apne1" {
  provider = aws.apne1

  topic_arn = aws_sns_topic.ssm_topic_apne1.arn
  protocol  = "lambda"
  endpoint  = module.lambda_function.lambda_function_arn
}

# apne3
resource "aws_sns_topic" "ssm_topic_apne3" {
  provider = aws.apne3
  name     = var.topic_name
}

resource "aws_sns_topic_subscription" "user_updates_sqs_target_apne3" {
  provider = aws.apne3

  topic_arn = aws_sns_topic.ssm_topic_apne3.arn
  protocol  = "lambda"
  endpoint  = module.lambda_function.lambda_function_arn
}

# aps1
resource "aws_sns_topic" "ssm_topic_aps1" {
  provider = aws.aps1
  name     = var.topic_name
}

resource "aws_sns_topic_subscription" "user_updates_sqs_target_aps1" {
  provider = aws.aps1

  topic_arn = aws_sns_topic.ssm_topic_aps1.arn
  protocol  = "lambda"
  endpoint  = module.lambda_function.lambda_function_arn
}

# apse1
resource "aws_sns_topic" "ssm_topic_apse1" {
  provider = aws.apse1
  name     = var.topic_name
}

resource "aws_sns_topic_subscription" "user_updates_sqs_target_apse1" {
  provider = aws.apse1

  topic_arn = aws_sns_topic.ssm_topic_apse1.arn
  protocol  = "lambda"
  endpoint  = module.lambda_function.lambda_function_arn
}

# apse2
resource "aws_sns_topic" "ssm_topic_apse2" {
  provider = aws.apse2
  name     = var.topic_name
}

resource "aws_sns_topic_subscription" "user_updates_sqs_target_apse2" {
  provider = aws.apse2

  topic_arn = aws_sns_topic.ssm_topic_apse2.arn
  protocol  = "lambda"
  endpoint  = module.lambda_function.lambda_function_arn
}

# cac1
resource "aws_sns_topic" "ssm_topic_cac1" {
  provider = aws.cac1
  name     = var.topic_name
}

resource "aws_sns_topic_subscription" "user_updates_sqs_target_cac1" {
  provider = aws.cac1

  topic_arn = aws_sns_topic.ssm_topic_cac1.arn
  protocol  = "lambda"
  endpoint  = module.lambda_function.lambda_function_arn
}

# euc1
resource "aws_sns_topic" "ssm_topic_euc1" {
  provider = aws.euc1
  name     = var.topic_name
}

resource "aws_sns_topic_subscription" "user_updates_sqs_target_euc1" {
  provider = aws.euc1

  topic_arn = aws_sns_topic.ssm_topic_euc1.arn
  protocol  = "lambda"
  endpoint  = module.lambda_function.lambda_function_arn
}

# eun1
resource "aws_sns_topic" "ssm_topic_eun1" {
  provider = aws.eun1
  name     = var.topic_name
}

resource "aws_sns_topic_subscription" "user_updates_sqs_target_eun1" {
  provider = aws.eun1

  topic_arn = aws_sns_topic.ssm_topic_eun1.arn
  protocol  = "lambda"
  endpoint  = module.lambda_function.lambda_function_arn
}

# euw1
resource "aws_sns_topic" "ssm_topic_euw1" {
  provider = aws.euw1
  name     = var.topic_name
}

resource "aws_sns_topic_subscription" "user_updates_sqs_target_euw1" {
  provider = aws.euw1

  topic_arn = aws_sns_topic.ssm_topic_euw1.arn
  protocol  = "lambda"
  endpoint  = module.lambda_function.lambda_function_arn
}

# euw2
resource "aws_sns_topic" "ssm_topic_euw2" {
  provider = aws.euw2
  name     = var.topic_name
}

resource "aws_sns_topic_subscription" "user_updates_sqs_target_euw2" {
  provider = aws.euw2

  topic_arn = aws_sns_topic.ssm_topic_euw2.arn
  protocol  = "lambda"
  endpoint  = module.lambda_function.lambda_function_arn
}

# euw3
resource "aws_sns_topic" "ssm_topic_euw3" {
  provider = aws.euw3
  name     = var.topic_name
}

resource "aws_sns_topic_subscription" "user_updates_sqs_target_euw3" {
  provider = aws.euw3

  topic_arn = aws_sns_topic.ssm_topic_euw3.arn
  protocol  = "lambda"
  endpoint  = module.lambda_function.lambda_function_arn
}

# sae1
resource "aws_sns_topic" "ssm_topic_sae1" {
  provider = aws.sae1
  name     = var.topic_name
}

resource "aws_sns_topic_subscription" "user_updates_sqs_target_sae1" {
  provider = aws.sae1

  topic_arn = aws_sns_topic.ssm_topic_sae1.arn
  protocol  = "lambda"
  endpoint  = module.lambda_function.lambda_function_arn
}

# use2
resource "aws_sns_topic" "ssm_topic_use2" {
  provider = aws.use2
  name     = var.topic_name
}

resource "aws_sns_topic_subscription" "user_updates_sqs_target_use2" {
  provider = aws.use2

  topic_arn = aws_sns_topic.ssm_topic_use2.arn
  protocol  = "lambda"
  endpoint  = module.lambda_function.lambda_function_arn
}

# usw1
resource "aws_sns_topic" "ssm_topic_usw1" {
  provider = aws.usw1
  name     = var.topic_name
}

resource "aws_sns_topic_subscription" "user_updates_sqs_target_usw1" {
  provider = aws.usw1

  topic_arn = aws_sns_topic.ssm_topic_usw1.arn
  protocol  = "lambda"
  endpoint  = module.lambda_function.lambda_function_arn
}

# usw2
resource "aws_sns_topic" "ssm_topic_usw2" {
  provider = aws.usw2
  name     = var.topic_name
}

resource "aws_sns_topic_subscription" "user_updates_sqs_target_usw2" {
  provider = aws.usw2

  topic_arn = aws_sns_topic.ssm_topic_usw2.arn
  protocol  = "lambda"
  endpoint  = module.lambda_function.lambda_function_arn
}