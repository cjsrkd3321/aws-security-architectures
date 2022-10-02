resource "aws_rolesanywhere_trust_anchor" "this" {
  name    = "${var.org}-trust-anchor"
  enabled = var.trust_anchor_enabled
  source {
    source_data {
      x509_certificate_data = tls_self_signed_cert.root_ca.cert_pem
    }
    source_type = "CERTIFICATE_BUNDLE"
  }
}

resource "aws_rolesanywhere_profile" "this" {
  name    = "${var.org}-profile"
  enabled = var.profile_enabled
  session_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = [
        "*"
      ]
      Effect   = "Allow"
      Resource = ["*"]

      Condition = {
        IpAddressIfExists = {
          "aws:SourceIp"    = var.public_ip_ranges
          "aws:VpcSourceIp" = ["10.0.0.0/8", "172.16.0.0/12"]
        }
      }
    }]
  })
  role_arns = [for role in aws_iam_role.this : role.arn]
}