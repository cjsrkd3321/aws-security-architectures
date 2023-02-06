variable "patterns" {
  type = any
  default = {
    login-alarm            = <<PATTERN
    {
      "source": ["aws.signin"],
      "detail-type": ["AWS Console Sign In via CloudTrail"],
      "detail": {
        "eventSource": ["signin.amazonaws.com"],
        "eventName": ["ConsoleLogin"]
      }
    }
    PATTERN
    create-access-key      = <<PATTERN
    {
      "source": ["aws.iam"],
      "detail-type": ["AWS API Call via CloudTrail"],
      "detail": {
        "eventSource": ["iam.amazonaws.com"],
        "eventName": ["CreateAccessKey"]
      }
    }
    PATTERN
    sensitive-port-open    = <<PATTERN
    {
      "source": ["aws.ec2"],
      "detail-type": ["AWS API Call via CloudTrail"],
      "detail": {
        "eventSource": ["ec2.amazonaws.com"],
        "eventName": ["AuthorizeSecurityGroupIngress", "ModifySecurityGroupRules"]
      }
    }
    PATTERN
    ec2-state-notification = <<PATTERN
    {
      "source": ["aws.ec2"],
      "detail-type": ["EC2 Instance State-change Notification"]
    }
    PATTERN
  }
}

variable "hook_url" {
  type = string
}

variable "channel" {
  type = string
}