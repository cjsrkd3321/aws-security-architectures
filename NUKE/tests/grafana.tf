# GRAFANAWorkspaces
resource "aws_grafana_workspace" "this" {
  name                     = "nuke-grafana-workspace"
  account_access_type      = "CURRENT_ACCOUNT"
  authentication_providers = ["SAML"]
  permission_type          = "SERVICE_MANAGED"
  role_arn                 = aws_iam_role.grafana.arn
}
