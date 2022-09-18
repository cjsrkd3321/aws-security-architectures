resource "aws_cloudwatch_log_group" "test" {
  name              = "/aws/macie/classificationjobs"
  retention_in_days = 1
}

resource "aws_cloudwatch_log_subscription_filter" "test_lambdafunction_logfilter" {
  name            = "test_lambdafunction_logfilter"
  log_group_name  = aws_cloudwatch_log_group.test.name
  filter_pattern  = "{ $.eventType = \"JOB_COMPLETED\" }"
  destination_arn = module.lambda_function.lambda_function_arn
}