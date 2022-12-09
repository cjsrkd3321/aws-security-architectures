# EKSClusters
resource "aws_eks_cluster" "this" {
  name     = "nuke-eks-cluster"
  role_arn = aws_iam_role.eks_cluster.arn
  vpc_config {
    subnet_ids = [aws_subnet.this.id, aws_subnet.this2.id]
  }
  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_role_policy
  ]
}