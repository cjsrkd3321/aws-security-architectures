# RDSClusters
resource "aws_rds_cluster" "mysql" {
  cluster_identifier      = "nuke-aurora-mysql-cluster"
  engine                  = "aurora-mysql"
  db_subnet_group_name    = aws_db_subnet_group.this.name
  database_name           = "mydb"
  master_username         = "foo"
  master_password         = "nuke-rex.chun"
  backup_retention_period = 5
  preferred_backup_window = "07:00-09:00"
}

# RDSClusters
resource "aws_rds_cluster" "postgresql" {
  cluster_identifier      = "nuke-aurora-postgresql-cluster"
  engine                  = "aurora-postgresql"
  db_subnet_group_name    = aws_db_subnet_group.this.name
  database_name           = "mydb"
  master_username         = "foo"
  master_password         = "nuke-rex.chun"
  backup_retention_period = 5
  preferred_backup_window = "07:00-09:00"
}

resource "aws_db_subnet_group" "this" {
  name       = "main"
  subnet_ids = [aws_subnet.this.id, aws_subnet.this2.id, aws_subnet.this3.id]
}

# RDSClusterParameterGroups
resource "aws_rds_cluster_parameter_group" "this" {
  name   = "nuke-rds-cluster-pg"
  family = "aurora5.6"
  parameter {
    name  = "character_set_server"
    value = "utf8"
  }
  parameter {
    name  = "character_set_client"
    value = "utf8"
  }
}