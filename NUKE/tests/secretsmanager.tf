# SECRETSMANAGERSecrets
resource "aws_secretsmanager_secret" "this" {
  name = "nuke-secret"
}