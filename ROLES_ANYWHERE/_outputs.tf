output "trust_anchor_arn" {
  value = aws_rolesanywhere_trust_anchor.this.arn
}

output "profile_arn" {
  value = aws_rolesanywhere_profile.this.arn
}

output "role_arns" {
  value = [for role in aws_iam_role.this : role.arn]
}