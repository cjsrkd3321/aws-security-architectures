# SECRETSMANAGERSecrets
resource "aws_secretsmanager_secret" "this" {
  name = "nuke-secret-${random_string.this.id}"
}