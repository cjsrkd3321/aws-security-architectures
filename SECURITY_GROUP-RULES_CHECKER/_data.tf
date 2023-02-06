data "aws_caller_identity" "this" {}

data "aws_ami" "this" {
  most_recent = true

  filter {
    name   = "name"
    values = ["amzn2-ami-kernel-5.10-hvm-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["amazon"] # Canonical
}

data "http" "myip" {
  url = "http://ipv4.icanhazip.com"
}

data "aws_subnets" "this" {
  filter {
    name   = "vpc-id"
    values = [aws_default_vpc.default.id]
  }
}

data "aws_iam_policy_document" "this" {
  statement {
    sid = "AWSLogDeliveryWrite20150319"

    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["delivery.logs.amazonaws.com"]
    }

    actions = [
      "s3:PutObject",
    ]

    resources = [
      "${aws_s3_bucket.this.arn}/AWSLogs/*",
    ]

    condition {
      test     = "ArnLike"
      variable = "aws:SourceArn"
      values   = ["arn:aws:logs:ap-northeast-2:${data.aws_caller_identity.this.account_id}:*"]
    }

    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = ["${data.aws_caller_identity.this.account_id}"]
    }

    condition {
      test     = "StringEquals"
      variable = "s3:x-amz-acl"
      values   = ["bucket-owner-full-control"]
    }
  }

  statement {
    sid = "AWSLogDeliveryAclCheck"

    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["delivery.logs.amazonaws.com"]
    }

    actions = [
      "s3:GetBucketAcl",
    ]

    resources = [
      aws_s3_bucket.this.arn,
    ]

    condition {
      test     = "ArnLike"
      variable = "aws:SourceArn"
      values   = ["arn:aws:logs:ap-northeast-2:${data.aws_caller_identity.this.account_id}:*"]
    }

    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = ["${data.aws_caller_identity.this.account_id}"]
    }
  }
}