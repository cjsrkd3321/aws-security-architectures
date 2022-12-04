resource "aws_s3_bucket" "this" {
  bucket = "rex-${var.region}-nuke-${random_string.this.id}"
}

resource "aws_s3_bucket" "this2" {
  provider = aws.use1
  bucket   = "rex-${var.global_region}-nuke-${random_string.this.id}"

}