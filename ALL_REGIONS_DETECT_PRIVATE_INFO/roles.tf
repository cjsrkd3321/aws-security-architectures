resource "aws_iam_instance_profile" "profile" {
  name = "default-instance-profile"
  role = aws_iam_role.role.name
}

resource "aws_iam_role" "role" {
  name                = "default-instance-profile-role"
  managed_policy_arns = ["arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"]

  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": "sts:AssumeRole",
            "Principal": {
               "Service": "ec2.amazonaws.com"
            },
            "Effect": "Allow",
            "Sid": ""
        }
    ]
}
EOF

  inline_policy {
    name = "s3-put-object-policy"

    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Action   = ["s3:PutObject"]
          Effect   = "Allow"
          Resource = "${module.private_info_bucket.s3_bucket_arn}/*"
        },
      ]
    })
  }
}

# https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_passrole.html
resource "aws_iam_role" "sns_role" {
  name = "ssm-run-command-assume-role"

  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "",
            "Effect": "Allow",
            "Principal": {
                "Service": "ssm.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

  inline_policy {
    name = "sns-publish-policy"

    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Action   = ["sns:Publish"]
          Effect   = "Allow"
          Resource = "*"
        },
      ]
    })
  }
}