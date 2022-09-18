resource "aws_kms_key" "macie_export_key" {
  policy                  = data.aws_iam_policy_document.kms_policy.json
  enable_key_rotation     = true
  deletion_window_in_days = 7
  description             = "macie-export-key"
}

resource "aws_kms_alias" "alias" {
  name          = "alias/macie-export-key"
  target_key_id = aws_kms_key.macie_export_key.key_id
}