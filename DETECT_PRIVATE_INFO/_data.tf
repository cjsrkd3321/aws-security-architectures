data "aws_caller_identity" "current" {}

# https://aws.amazon.com/ko/premiumsupport/knowledge-center/macie-s3-kms-permission/
data "aws_iam_policy_document" "s3_policy" {
  statement {
    sid       = "Deny incorrect encryption header"
    effect    = "Deny"
    actions   = ["s3:PutObject"]
    resources = ["${module.s3_bucket.s3_bucket_arn}/*"]

    principals {
      type        = "Service"
      identifiers = ["macie.amazonaws.com"]
    }

    condition {
      test     = "StringNotEquals"
      variable = "s3:x-amz-server-side-encryption-aws-kms-key-id"
      values   = [aws_kms_key.macie_export_key.arn]
    }
  }

  statement {
    sid       = "Deny unencrypted object uploads"
    effect    = "Deny"
    actions   = ["s3:PutObject"]
    resources = ["${module.s3_bucket.s3_bucket_arn}/*"]

    principals {
      type        = "Service"
      identifiers = ["macie.amazonaws.com"]
    }

    condition {
      test     = "StringNotEquals"
      variable = "s3:x-amz-server-side-encryption"
      values   = ["aws:kms"]
    }
  }

  statement {
    sid       = "Allow Macie to upload objects to the bucket"
    effect    = "Allow"
    actions   = ["s3:PutObject"]
    resources = ["${module.s3_bucket.s3_bucket_arn}/*"]

    principals {
      type        = "Service"
      identifiers = ["macie.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [local.account_id]
    }

    condition {
      test     = "ArnLike"
      variable = "aws:SourceArn"
      values = [
        "arn:aws:macie2:us-east-1:${local.account_id}:export-configuration:*",
        "arn:aws:macie2:us-east-1:${local.account_id}:classification-job/*"
      ]
    }
  }

  statement {
    sid       = "Allow Macie to use the getBucketLocation operation"
    effect    = "Allow"
    actions   = ["s3:GetBucketLocation"]
    resources = [module.s3_bucket.s3_bucket_arn]

    principals {
      type        = "Service"
      identifiers = ["macie.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [local.account_id]
    }

    condition {
      test     = "ArnLike"
      variable = "aws:SourceArn"
      values = [
        "arn:aws:macie2:us-east-1:${local.account_id}:export-configuration:*",
        "arn:aws:macie2:us-east-1:${local.account_id}:classification-job/*"
      ]
    }
  }
}

# https://aws.amazon.com/ko/premiumsupport/knowledge-center/macie-s3-kms-permission/
data "aws_iam_policy_document" "kms_policy" {
  statement {
    sid       = "Enable IAM User Permissions"
    effect    = "Allow"
    actions   = ["kms:*"]
    resources = ["*"]

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${local.account_id}:root"]
    }
  }

  statement {
    effect    = "Allow"
    actions   = ["kms:GenerateDataKey", "kms:Encrypt"]
    resources = ["*"]

    principals {
      type        = "Service"
      identifiers = ["macie.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [local.account_id]
    }

    condition {
      test     = "ArnLike"
      variable = "aws:SourceArn"
      values = [
        "arn:aws:macie2:us-east-1:${local.account_id}:export-configuration:*",
        "arn:aws:macie2:us-east-1:${local.account_id}:classification-job/*"
      ]
    }
  }
}