# IAMUsers
# IAMUserPermissionsBoundaries
resource "aws_iam_user" "this" {
  name                 = "nuke-user"
  path                 = "/system/"
  permissions_boundary = aws_iam_policy.this.arn
}

# IAMLoginProfiles
resource "aws_iam_user_login_profile" "this" {
  user = aws_iam_user.this.name
}

# IAMUserAccessKeys
resource "aws_iam_access_key" "this" {
  user = aws_iam_user.this.name
}

# IAMUserSshKeys
resource "aws_iam_user_ssh_key" "user" {
  username   = aws_iam_user.this.name
  encoding   = "SSH"
  public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQD3F6tyPEFEzV0LX3X8BsXdMsQz1x2cEikKDEY0aIj41qgxMCP/iteneqXSIFZBp5vizPvaoIR3Um9xK7PGoW8giupGn+EPuxIA4cDM4vzOqOkiMPhz5XK0whEjkVzTo4+S0puvDZuwIsdiW9mxhJc7tgBNL0cYlWSYVkz4G/fslNfRPW5mYAM49f4fhtxPb5ok4Q2Lg9dPKVHO/Bgeu5woMc7RY0p1ej6D4CKFE6lymSDJpW0YHX/wqE9+cfEauh7xZcG0q9t2ta6F6fmX0agvpFyZo8aFbXeUBr7osSCJNgvavWbM/06niWrOvYX2xwWdhXmXSrbX8ZbabVohBK41 mytest@mydomain.com"
}

# IAMSigningCertificates
resource "aws_iam_signing_certificate" "this" {
  user_name        = aws_iam_user.this.name
  certificate_body = var.cert_body
}

# IAMServiceSpecificCredentials
resource "aws_iam_service_specific_credential" "this" {
  service_name = "codecommit.amazonaws.com"
  user_name    = aws_iam_user.this.name
}

# IAMServerCertificates
resource "aws_iam_server_certificate" "this" {
  name             = "nuke-cert"
  certificate_body = var.cert_body
  private_key      = var.private_key
}

# IAMUserPolicies
resource "aws_iam_user_policy" "this" {
  name   = "nuke-policy"
  user   = aws_iam_user.this.name
  policy = var.nuke_policy
}

# IAMUserPolicyAttachments
# IAMGroupPolicyAttachments
# IAMRolePolicyAttachments
resource "aws_iam_policy_attachment" "this" {
  name       = "nuke-attachment"
  users      = [aws_iam_user.this.name]
  roles      = [aws_iam_role.this.name]
  groups     = [aws_iam_group.this.name]
  policy_arn = aws_iam_policy.this.arn
}

# IAMPolicies
# IAMPolicyVersions
resource "aws_iam_policy" "this" {
  name        = "nuke-policy"
  description = "A test policy"
  policy      = var.nuke_policy
}

# IAMGroups
resource "aws_iam_group" "this" {
  name = "nuke-group"
  path = "/users/"
}

# IAMListUserGroupAttachments
resource "aws_iam_group_membership" "team" {
  name = "nuke-group-membership"
  users = [
    aws_iam_user.this.name,
  ]
  group = aws_iam_group.this.name
}

# IAMGroupPolicies
resource "aws_iam_group_policy" "this" {
  name   = "nuke-policy"
  group  = aws_iam_group.this.name
  policy = var.nuke_policy
}

# IAMRoles
resource "aws_iam_role" "this" {
  name = "nuke-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      },
    ]
  })
}

# IAMRoles
resource "aws_iam_role" "lambda" {
  name = "nuke-lambda"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

# IAMRolePolicies
resource "aws_iam_role_policy" "this" {
  name   = "nuke-policy"
  role   = aws_iam_role.this.id
  policy = var.nuke_policy
}

# IAMInstanceProfiles
# IAMInstanceProfileRoles
resource "aws_iam_instance_profile" "this" {
  name = "nuke-profile"
  role = aws_iam_role.this.name
}

# IAMOpenIdConnectProviders
resource "aws_iam_openid_connect_provider" "this" {
  url = "https://accounts.google.com"
  client_id_list = [
    "266362248691-342342xasdasdasda-apps.googleusercontent.com",
  ]
  thumbprint_list = []
}