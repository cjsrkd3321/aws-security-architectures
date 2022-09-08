data "aws_iam_policy_document" "event_bus_invoke_remote_event_bus" {
  statement {
    effect    = "Allow"
    actions   = ["events:PutEvents"]
    resources = ["arn:aws:events:us-east-1:${local.account_id}:event-bus/default"]
  }
}

data "aws_caller_identity" "current" {}