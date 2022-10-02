resource "aws_iam_role" "this" {
  for_each = var.users
  name     = "${each.key}-rolesanywhere-role"

  managed_policy_arns = each.value["managed_policy_arns"]

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

resource "aws_iam_role_policy" "this" {
  for_each = var.users

  role = aws_iam_role.this[each.key].id

  name   = "${each.key}-additional-inline-policy"
  policy = data.aws_iam_policy_document.override[each.key].json
}

data "aws_iam_policy_document" "base" {
  for_each = var.users

  statement {
    sid       = "BaseIpDenyAccess"
    actions   = ["*"]
    resources = ["*"]
    effect    = "Deny"

    condition {
      test     = "NotIpAddressIfExists"
      variable = "aws:SourceIp"
      values   = each.value["public_ips"]
    }

    condition {
      test     = "NotIpAddressIfExists"
      variable = "aws:VpcSourceIp"
      values   = each.value["private_ips"]
    }
  }
}

data "aws_iam_policy_document" "override" {
  for_each = var.users

  override_policy_documents = [data.aws_iam_policy_document.base[each.key].json, jsonencode(each.value["inline_policy"])]
}