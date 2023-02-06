variable "log_format" {
  type    = string
  default = "$${flow-direction} $${protocol} $${srcaddr} $${dstaddr} $${dstport} $${action} $${log-status} $${tcp-flags} $${type} $${start} $${end}"
}

variable "scheduled_rule_name" {
  type    = string
  default = "sg-checker-schedule-rule"
}

variable "lambda_name" {
  type    = string
  default = "security-group-rules-checker"
}

variable "vpc_flow_log_bucket_name" {
  type    = string
  default = "rex-vpcflow-log-bucket-s3"
}

variable "athena_workgroup_name" {
  type    = string
  default = "vpcflowlogs"
}

variable "athena_query_results_bucket_name" {
  type    = string
  default = "rex-vpcflow-log-results-s3"
}