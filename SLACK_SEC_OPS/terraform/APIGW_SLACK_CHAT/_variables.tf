variable "slack_signing_secret" {
  type      = string
  sensitive = true
}

variable "slack_oauth_token" {
  type      = string
  sensitive = true
}

variable "manager" {
  type = string
}

variable "path" {
  type    = string
  default = "slack"
}