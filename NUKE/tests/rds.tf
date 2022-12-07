resource "aws_rds_cluster" "mysql" {
  cluster_identifier      = "nuke-aurora-mysql-cluster"
  engine                  = "aurora-mysql"
  availability_zones      = ["${var.region}a", "${var.region}b"]
  database_name           = "mydb"
  master_username         = "foo"
  master_password         = "nuke-rex.chun"
  backup_retention_period = 5
  preferred_backup_window = "07:00-09:00"
}

resource "aws_rds_cluster" "postgresql" {
  cluster_identifier      = "nuke-aurora-postgresql-cluster"
  engine                  = "aurora-postgresql"
  availability_zones      = ["${var.region}a", "${var.region}b"]
  database_name           = "mydb"
  master_username         = "foo"
  master_password         = "nuke-rex.chun"
  backup_retention_period = 5
  preferred_backup_window = "07:00-09:00"
}