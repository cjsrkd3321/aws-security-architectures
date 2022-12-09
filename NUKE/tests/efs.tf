# EFSFilesystems
resource "aws_efs_file_system" "this" {
  creation_token = "nuke-efs-file-system"
}