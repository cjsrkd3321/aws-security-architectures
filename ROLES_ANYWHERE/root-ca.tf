resource "tls_private_key" "root_ca" {
  algorithm = var.key_algorithm
  rsa_bits  = var.key_bits
}

resource "tls_cert_request" "root_ca" {
  private_key_pem = tls_private_key.root_ca.private_key_pem

  subject {
    common_name  = "${var.org} Self Signehd CA"
    organization = "${var.org}, Inc"
  }
}

resource "tls_self_signed_cert" "root_ca" {
  private_key_pem   = tls_private_key.root_ca.private_key_pem
  is_ca_certificate = true

  subject {
    common_name  = "${var.org} Self Signehd CA"
    organization = "${var.org}, Inc"
  }

  validity_period_hours = var.root_cert_validity_period_hours

  allowed_uses = var.root_cert_allowed_uses
}