module "lambda_function" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = var.lambda_name
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.9"

  source_path = "func"

  timeout       = 30
  memory_size   = 2048
  architectures = ["arm64"]

  publish = true
  allowed_triggers = {
    S3QueryResults = {
      principal  = "s3.amazonaws.com"
      source_arn = "${aws_s3_bucket.results.arn}"
    }
    EventBridge = {
      principal  = "events.amazonaws.com"
      source_arn = "${aws_cloudwatch_event_rule.this.arn}"
    }
  }

  cloudwatch_logs_retention_in_days = 1

  environment_variables = {
    VPC_FLOW_LOG_BUCKET = aws_s3_bucket.this.id
    WORKGROUP           = aws_athena_workgroup.this.id
  }

  attach_policy = true
  policy        = "arn:aws:iam::aws:policy/AmazonAthenaFullAccess"

  attach_policy_json = true
  policy_json        = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
      {
        "Effect": "Allow",
        "Action": [
            "ec2:CreateTags",
            "ec2:DescribeTags",
            "ec2:DescribeSecurityGroupRules",
            "ec2:DescribeNetworkInterfaces"
        ],
        "Resource": ["*"]
      },
      {
        "Effect": "Allow",
        "Action": [
          "athena:ListTableMetadata",
          "athena:StartQueryExecution"
        ],
        "Resource": ["*"]
      },
      {
        "Effect": "Allow",
        "Action": [
          "s3:GetObject",
          "s3:PutObject"
        ],
        "Resource": ["${aws_s3_bucket.this.arn}/*", "${aws_s3_bucket.results.arn}/*"]
      }
  ]
}
EOF
}