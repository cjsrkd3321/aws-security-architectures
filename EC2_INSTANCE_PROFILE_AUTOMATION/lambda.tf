module "lambda_function" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "ec2-instance-profile-automation"
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.9"

  source_path = "func"

  timeout     = 60
  memory_size = 256

  publish = true
  allowed_triggers = {
    EventBridge = {
      principal  = "events.amazonaws.com"
      source_arn = aws_cloudwatch_event_rule.eventbridge_rule.arn
    }
  }

  environment_variables = {
    EC2_DEFAULT_ROLE      = aws_iam_role.ec2_default_role.name
    SSM_MANAGED_POLICY    = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
    INSTANCE_PROFILE_ARN  = aws_iam_instance_profile.instance_profile.arn
    INSTANCE_PROFILE_NAME = aws_iam_instance_profile.instance_profile.name
  }

  attach_policy_json = true
  policy_json        = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "ec2:DescribeIamInstanceProfileAssociations", 
                "ec2:DescribeInstances",
                "ec2:AssociateIamInstanceProfile",
                "ec2:DescribeRegions",
                "iam:GetInstanceProfile", 
                "iam:ListAttachedRolePolicies", 
                "iam:AttachRolePolicy",
                "iam:PassRole"
            ],
            "Resource": ["*"],
            "Effect": "Allow"
        }
    ]
}
EOF
}