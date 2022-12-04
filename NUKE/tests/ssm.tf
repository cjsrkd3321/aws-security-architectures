# SSMParameters
resource "aws_ssm_parameter" "this" {
  name  = "nuke"
  type  = "String"
  value = "parameter"
}