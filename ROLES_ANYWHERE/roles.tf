resource "aws_iam_role" "this" {
  for_each = var.users
  name     = "${each.key}-rolesanywhere-role"

  inline_policy {
    name = "${each.key}-inline-policy"

    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Action   = ["*"]
          Effect   = "Deny"
          Resource = "*"
          Condition = {
            NotIpAddress = {
              "aws:SourceIp" : each.value
            }
          }
        },
      ]
    })
  }

  managed_policy_arns = []

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "rolesanywhere.amazonaws.com"
        },
        Action = [
          "sts:AssumeRole",
          "sts:SetSourceIdentity",
          "sts:TagSession"
        ],
        Condition = {
          StringEquals = {
            "aws:PrincipalTag/x509Subject/CN" : each.key
          }
        }
      }
    ]
  })
}