variable "users" {
  description = "User names and IPs. This variable will update someday."
  type        = map(string)
  default = {
    "rex.chun" : "1.1.1.1/32"
  }
}

variable "org" {
  type    = string
  default = "rexchun"
}

# https://docs.aws.amazon.com/rolesanywhere/latest/userguide/trust-model.html#signature-verification
variable "root_cert_allowed_uses" {
  type = list(string)
  default = [
    "crl_signing",
    "cert_signing",
    "digital_signature",
  ]
}

variable "user_cert_allowed_uses" {
  type = list(string)
  default = [
    "digital_signature",
  ]
}

variable "root_cert_validity_period_hours" {
  type    = number
  default = 24 * 365 * 10 # 10 years
}

variable "user_cert_validity_period_hours" {
  type    = number
  default = 24 * 365 * 5 # 5 years
}

variable "trust_anchor_enabled" {
  type    = bool
  default = true
}

variable "profile_enabled" {
  type    = bool
  default = true
}

variable "key_algorithm" {
  type    = string
  default = "RSA"
}

variable "key_bits" {
  type    = number
  default = 4096
}