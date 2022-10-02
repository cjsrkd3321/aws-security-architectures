variable "public_ip_ranges" {
  type    = list(string)
  default = ["1.1.1.0/24"]
}

variable "users" {
  description = "User names, policies and IPs"
  type = map(object({
    public_ips          = list(string)
    private_ips         = list(string)
    managed_policy_arns = list(string)
    inline_policy       = map(any)
  }))
  default = {
    "rex.chun" : {
      public_ips          = ["1.1.1.1/32"]
      private_ips         = []
      managed_policy_arns = ["arn:aws:iam::aws:policy/ReadOnlyAccess"]
      inline_policy = {
        Statement = [
          {
            Action   = ["sts:GetCallerIdentity"] # This is no meaning(GetCallerIdentity API can call always whether has permission or not)
            Effect   = "Allow"
            Resource = "*"
          },
        ]
      }
    }
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