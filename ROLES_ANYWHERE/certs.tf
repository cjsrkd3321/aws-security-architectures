resource "tls_private_key" "user_keys" {
  for_each  = var.users
  algorithm = var.key_algorithm
  rsa_bits  = var.key_bits
}

resource "tls_cert_request" "user_csrs" {
  for_each        = var.users
  private_key_pem = tls_private_key.user_keys[each.key].private_key_pem

  subject {
    common_name  = each.key
    organization = var.org
  }
}

resource "tls_locally_signed_cert" "user_certs" {
  for_each           = var.users
  cert_request_pem   = tls_cert_request.user_csrs[each.key].cert_request_pem
  ca_private_key_pem = tls_private_key.root_ca.private_key_pem
  ca_cert_pem        = tls_self_signed_cert.root_ca.cert_pem

  validity_period_hours = var.user_cert_validity_period_hours

  allowed_uses = var.user_cert_allowed_uses
}

resource "local_sensitive_file" "cert_files" {
  for_each        = var.users
  content         = tls_locally_signed_cert.user_certs[each.key].cert_pem
  filename        = "${each.key}.crt"
  file_permission = "0400"
}

resource "local_sensitive_file" "key_files" {
  for_each        = var.users
  content         = tls_private_key.user_keys[each.key].private_key_pem
  filename        = "${each.key}.key"
  file_permission = "0400"
}