module "lambda_function" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "security-alarm-lambda"
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.9"

  source_path = "func"

  timeout     = 60
  memory_size = 256

  cloudwatch_logs_retention_in_days = 1

  environment_variables = {
    SLACK_HOOK_URL  = var.hook_url 
    SLACK_CHANNEL   = var.channel  
    SOURCE_IPS      = "[\"YOUR_IP\", \"AWS Internal\"]"
    SENSITIVE_PORTS = "[22, 3389]"
    ALLOWED_IPS     = "[\"10.0.0.0/8\", \"172.16.0.0/12\", \"192.168.0.0/16\"]"
  }
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  for_each = aws_cloudwatch_event_rule.use1

  action        = "lambda:InvokeFunction"
  function_name = module.lambda_function.lambda_function_name
  principal     = "events.amazonaws.com"
  source_arn    = each.value.arn
}