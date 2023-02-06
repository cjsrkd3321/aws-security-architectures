resource "aws_athena_workgroup" "this" {
  name          = var.athena_workgroup_name
  force_destroy = true
  configuration {
    enforce_workgroup_configuration    = false
    publish_cloudwatch_metrics_enabled = false
    bytes_scanned_cutoff_per_query     = 1099511627776000 # 1000 TB

    result_configuration {
      output_location = "s3://${aws_s3_bucket.results.bucket}/"
    }
  }
}

resource "aws_s3_bucket" "results" {
  bucket        = var.athena_query_results_bucket_name
  force_destroy = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "results" {
  bucket = aws_s3_bucket.results.bucket

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_notification" "results" {
  bucket = aws_s3_bucket.results.id

  lambda_function {
    lambda_function_arn = module.lambda_function.lambda_function_arn
    events              = ["s3:ObjectCreated:Put"]
    filter_suffix       = ".csv"
  }

  depends_on = [
    module.lambda_function
  ]
}