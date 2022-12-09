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

# EKSNodeGroups
resource "aws_eks_node_group" "this" {
  cluster_name    = aws_eks_cluster.this.name
  node_group_name = "nuke-eks-node-group"
  node_role_arn   = aws_iam_role.eks_cluster.arn
  subnet_ids      = [aws_subnet.this.id, aws_subnet.this2.id]
  scaling_config {
    desired_size = 1
    max_size     = 2
    min_size     = 1
  }
  update_config {
    max_unavailable = 1
  }
}