locals {
  account_id      = data.aws_caller_identity.current.account_id
  default_bus_arn = "arn:aws:events:us-east-1:${local.account_id}:event-bus/default"
}