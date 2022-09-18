resource "aws_macie2_account" "this" {}

resource "aws_macie2_classification_export_configuration" "this" {
  depends_on = [
    aws_macie2_account.this,
  ]
  s3_destination {
    bucket_name = module.s3_bucket.s3_bucket_id
    kms_key_arn = aws_kms_key.macie_export_key.arn
  }
}

resource "aws_macie2_custom_data_identifier" "this" {
  name        = "주민등록번호"
  regex       = "\\d{2}([0]\\d|[1][0-2])([0][1-9]|[1-2]\\d|[3][0-1])[-]*[1-4]\\d{6}"
  description = "주민등록번호"

  depends_on = [aws_macie2_account.this]
}