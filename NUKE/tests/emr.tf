# EMRClusters
resource "aws_emr_cluster" "this" {
  name          = "nuke-emr-cluster"
  release_label = "emr-4.6.0"
  applications  = ["Spark"]

  additional_info = <<EOF
{
  "instanceAwsClientConfiguration": {
    "proxyPort": 8099,
    "proxyHost": "myproxy.example.com"
  }
}
EOF

  termination_protection            = false
  keep_job_flow_alive_when_no_steps = true

  ec2_attributes {
    subnet_id        = aws_subnet.this.id
    instance_profile = aws_iam_instance_profile.emr_profile.arn
  }

  master_instance_group {
    instance_type = "m4.large"
  }

  core_instance_group {
    instance_type  = "c4.large"
    instance_count = 1
    ebs_config {
      size                 = "40"
      type                 = "gp2"
      volumes_per_instance = 1
    }
    bid_price = "0.30"
  }
  ebs_root_volume_size = 100
  bootstrap_action {
    path = "s3://elasticmapreduce/bootstrap-actions/run-if"
    name = "runif"
    args = ["instance.isMaster=true", "echo running on master node"]
  }
  configurations_json = <<EOF
  [
    {
      "Classification": "hadoop-env",
      "Configurations": [
        {
          "Classification": "export",
          "Properties": {
            "JAVA_HOME": "/usr/lib/jvm/java-1.8.0"
          }
        }
      ],
      "Properties": {}
    },
    {
      "Classification": "spark-env",
      "Configurations": [
        {
          "Classification": "export",
          "Properties": {
            "JAVA_HOME": "/usr/lib/jvm/java-1.8.0"
          }
        }
      ],
      "Properties": {}
    }
  ]
EOF
  service_role        = aws_iam_role.emr_cluster.arn
}