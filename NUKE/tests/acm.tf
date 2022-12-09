# ACMCertificates
resource "aws_acm_certificate" "this" {
  domain_name       = "nuke-acm-certificates.com"
  validation_method = "DNS"
  lifecycle {
    create_before_destroy = true
  }
}

# # ACMPCACertificateAuthorities
# resource "aws_acmpca_certificate_authority" "this" {
#   certificate_authority_configuration {
#     key_algorithm     = "RSA_4096"
#     signing_algorithm = "SHA512WITHRSA"
#     subject {
#       common_name = "nuke-acmpca-certificates.com"
#     }
#   }
#   permanent_deletion_time_in_days = 7
# }
