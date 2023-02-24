resource "random_string" "suffix" {
  length  = 8
  special = false
  upper   = false
}

module "s3_bucket" {
  source = "terraform-aws-modules/s3-bucket/aws"

  bucket        = "macie-result-bucket-${random_string.suffix.result}"
  force_destroy = true

  attach_deny_insecure_transport_policy = true
  attach_require_latest_tls_policy      = true

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true

  attach_policy = true
  policy        = data.aws_iam_policy_document.s3_policy.json

  control_object_ownership = true
  object_ownership         = "BucketOwnerEnforced"

  expected_bucket_owner = local.account_id

  server_side_encryption_configuration = {
    rule = {
      apply_server_side_encryption_by_default = {
        sse_algorithm = "AES256"
      }
      bucket_key_enabled = true,
    }
  }

  lifecycle_rule = [
    {
      id      = "macie-log"
      enabled = true
      expiration = {
        days                         = 1
        expired_object_delete_marker = false
      }
      noncurrent_version_expiration = {
        days = 1
      }
      abort_incomplete_multipart_upload_days = 1
    }
  ]
}

module "private_info_bucket" {
  source = "terraform-aws-modules/s3-bucket/aws"

  bucket        = "private-info-bucket-${random_string.suffix.result}"
  force_destroy = true

  attach_deny_insecure_transport_policy = true
  attach_require_latest_tls_policy      = true

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true

  #   attach_policy = true
  #   policy        = data.aws_iam_policy_document.s3_policy.json

  control_object_ownership = true
  object_ownership         = "BucketOwnerEnforced"

  expected_bucket_owner = local.account_id

  server_side_encryption_configuration = {
    rule = {
      apply_server_side_encryption_by_default = {
        sse_algorithm = "AES256"
      }
      bucket_key_enabled = true,
    }
  }

  lifecycle_rule = [
    {
      id      = "private-info-rule"
      enabled = true
      expiration = {
        days                         = 1
        expired_object_delete_marker = false
      }
      noncurrent_version_expiration = {
        days = 1
      }
      abort_incomplete_multipart_upload_days = 1
    }
  ]
}

module "detect_result_bucket" {
  source = "terraform-aws-modules/s3-bucket/aws"

  bucket        = "detect-result-bucket-${random_string.suffix.result}"
  force_destroy = true

  attach_deny_insecure_transport_policy = true
  attach_require_latest_tls_policy      = true

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true

  #   attach_policy = true
  #   policy        = data.aws_iam_policy_document.s3_policy.json

  control_object_ownership = true
  object_ownership         = "BucketOwnerEnforced"

  expected_bucket_owner = local.account_id

  server_side_encryption_configuration = {
    rule = {
      apply_server_side_encryption_by_default = {
        sse_algorithm = "AES256"
      }
      bucket_key_enabled = true,
    }
  }

  lifecycle_rule = [
    {
      id      = "detect-result"
      enabled = true
      expiration = {
        days                         = 1
        expired_object_delete_marker = false
      }
      noncurrent_version_expiration = {
        days = 1
      }
      abort_incomplete_multipart_upload_days = 1
    }
  ]
}