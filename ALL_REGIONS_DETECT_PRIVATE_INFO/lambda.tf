module "lambda_function" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "macie-analyzer-lambda"
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.9"

  source_path = "func"

  timeout       = 60
  memory_size   = 512
  architectures = ["arm64"]

  publish = true
  allowed_triggers = {
    CloudwatchLogs = {
      principal  = "logs.us-east-1.amazonaws.com"
      source_arn = "${aws_cloudwatch_log_group.test.arn}:*"
    }
    EventBridge = {
      principal  = "events.amazonaws.com"
      source_arn = aws_cloudwatch_event_rule.use1.arn
    }
    EventBridge-warm = {
      principal  = "events.amazonaws.com"
      source_arn = aws_cloudwatch_event_rule.use1_warm.arn
    }
    SNS = {
      principal  = "sns.amazonaws.com"
      source_arn = aws_sns_topic.ssm_topic.arn
    }
    SNS-apne2 = {
      principal  = "sns.amazonaws.com"
      source_arn = aws_sns_topic.ssm_topic_apne2.arn
    }
    SNS-apne1 = {
      principal  = "sns.amazonaws.com"
      source_arn = aws_sns_topic.ssm_topic_apne1.arn
    }
    SNS-apne3 = {
      principal  = "sns.amazonaws.com"
      source_arn = aws_sns_topic.ssm_topic_apne3.arn
    }
    SNS-aps1 = {
      principal  = "sns.amazonaws.com"
      source_arn = aws_sns_topic.ssm_topic_aps1.arn
    }
    SNS-apse1 = {
      principal  = "sns.amazonaws.com"
      source_arn = aws_sns_topic.ssm_topic_apse1.arn
    }
    SNS-apse2 = {
      principal  = "sns.amazonaws.com"
      source_arn = aws_sns_topic.ssm_topic_apse2.arn
    }
    SNS-cac1 = {
      principal  = "sns.amazonaws.com"
      source_arn = aws_sns_topic.ssm_topic_cac1.arn
    }
    SNS-euc1 = {
      principal  = "sns.amazonaws.com"
      source_arn = aws_sns_topic.ssm_topic_euc1.arn
    }
    SNS-eun1 = {
      principal  = "sns.amazonaws.com"
      source_arn = aws_sns_topic.ssm_topic_eun1.arn
    }
    SNS-euw1 = {
      principal  = "sns.amazonaws.com"
      source_arn = aws_sns_topic.ssm_topic_euw1.arn
    }
    SNS-euw2 = {
      principal  = "sns.amazonaws.com"
      source_arn = aws_sns_topic.ssm_topic_euw2.arn
    }
    SNS-euw3 = {
      principal  = "sns.amazonaws.com"
      source_arn = aws_sns_topic.ssm_topic_euw3.arn
    }
    SNS-sae1 = {
      principal  = "sns.amazonaws.com"
      source_arn = aws_sns_topic.ssm_topic_sae1.arn
    }
    SNS-use2 = {
      principal  = "sns.amazonaws.com"
      source_arn = aws_sns_topic.ssm_topic_use2.arn
    }
    SNS-usw1 = {
      principal  = "sns.amazonaws.com"
      source_arn = aws_sns_topic.ssm_topic_usw1.arn
    }
    SNS-usw2 = {
      principal  = "sns.amazonaws.com"
      source_arn = aws_sns_topic.ssm_topic_usw2.arn
    }
  }

  cloudwatch_logs_retention_in_days = 1

  environment_variables = {
    SLACK_HOOK_URL       = var.hook_url
    SLACK_CHANNEL        = var.channel
    SNS_ASSUME_ROLE_ARN  = aws_iam_role.sns_role.arn
    SNS_TOPIC_ARN        = aws_sns_topic.ssm_topic.arn
    PRIAVTE_INFO_BUCKET  = module.private_info_bucket.s3_bucket_arn
    RESULT_BUCKET        = module.detect_result_bucket.s3_bucket_arn
    S3_ACCOUNT_ID        = data.aws_caller_identity.current.account_id
    EVENTBRIDGE_WARM_ARN = aws_cloudwatch_event_rule.use1_warm.arn
  }

  attach_policy_json = true
  policy_json        = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
      {
        "Effect": "Allow",
        "Action": [
            "ec2:DescribeInstances",
            "ec2:DescribeRegions",
            "ssm:SendCommand",
            "ssm:GetConnectionStatus",
            "iam:PassRole"
        ],
        "Resource": ["*"]
      },
      {
        "Effect": "Allow",
        "Action": [
          "macie2:ListFindings",
          "macie2:ListCustomDataIdentifiers",
          "macie2:GetFindings",
          "macie2:CreateClassificationJob"
        ],
        "Resource": ["*"]
      },
      {
        "Effect": "Allow",
        "Action": [
          "kms:Decrypt"
        ],
        "Resource": ["${aws_kms_key.macie_export_key.arn}"]
      },
      {
        "Effect": "Allow",
        "Action": [
          "s3:GetObject",
          "s3:ListBucket"
        ],
        "Resource": [
          "${module.s3_bucket.s3_bucket_arn}", 
          "${module.private_info_bucket.s3_bucket_arn}",
          "${module.s3_bucket.s3_bucket_arn}/*", 
          "${module.private_info_bucket.s3_bucket_arn}/*"
        ]
      },
      {
        "Effect": "Allow",
        "Action": [
          "s3:PutObject"
        ],
        "Resource": [
          "${module.detect_result_bucket.s3_bucket_arn}",
          "${module.detect_result_bucket.s3_bucket_arn}/*"
        ]
      }
  ]
}
EOF
}