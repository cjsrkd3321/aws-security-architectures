output "instance_profile_arn" {
  value = aws_iam_instance_profile.instance_profile.arn
}

output "instance_profile_name" {
  value = aws_iam_instance_profile.instance_profile.name
}