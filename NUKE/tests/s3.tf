# S3Buckets
resource "aws_s3_bucket" "this" {
  bucket = "rex-${var.region}-nuke-${random_string.this.id}"
}

# S3Buckets
resource "aws_s3_bucket" "this2" {
  provider = aws.use1
  bucket   = "rex-${var.global_region}-nuke-${random_string.this.id}"
}

# S3Objects
resource "aws_s3_object" "this" {
  bucket = aws_s3_bucket.this.bucket
  key    = "nuke-object"
  source = "resources/nuke_lambda.zip"
  etag   = filemd5("resources/nuke_lambda.zip")
}