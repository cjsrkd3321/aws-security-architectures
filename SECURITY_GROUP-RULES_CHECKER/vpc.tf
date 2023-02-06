resource "aws_flow_log" "this" {
  vpc_id                   = aws_default_vpc.default.id
  log_destination_type     = "s3"
  log_destination          = aws_s3_bucket.this.arn
  log_format               = var.log_format
  traffic_type             = "ACCEPT"
  max_aggregation_interval = 60

  destination_options {
    file_format        = "plain-text"
    per_hour_partition = false
  }
}

resource "aws_default_vpc" "default" {}

