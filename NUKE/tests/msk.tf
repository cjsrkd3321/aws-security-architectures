# # MSKClusters
# resource "aws_msk_cluster" "this" {
#   cluster_name           = "nuke-cluster"
#   kafka_version          = "3.2.0"
#   number_of_broker_nodes = 3
#   broker_node_group_info {
#     instance_type = "kafka.m5.large"
#     client_subnets = [
#       aws_subnet.this.id,
#       aws_subnet.this2.id,
#       aws_subnet.this3.id,
#     ]
#     storage_info {
#       ebs_storage_info {
#         volume_size = 1
#       }
#     }
#     security_groups = [aws_security_group.this.id]
#   }
#   encryption_info {
#     encryption_at_rest_kms_key_arn = aws_kms_key.this.arn
#   }
# }