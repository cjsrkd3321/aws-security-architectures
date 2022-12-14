resource "aws_key_pair" "this" {
  key_name   = "nuke-key-pair"
  public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQD3F6tyPEFEzV0LX3X8BsXdMsQz1x2cEikKDEY0aIj41qgxMCP/iteneqXSIFZBp5vizPvaoIR3Um9xK7PGoW8giupGn+EPuxIA4cDM4vzOqOkiMPhz5XK0whEjkVzTo4+S0puvDZuwIsdiW9mxhJc7tgBNL0cYlWSYVkz4G/fslNfRPW5mYAM49f4fhtxPb5ok4Q2Lg9dPKVHO/Bgeu5woMc7RY0p1ej6D4CKFE6lymSDJpW0YHX/wqE9+cfEauh7xZcG0q9t2ta6F6fmX0agvpFyZo8aFbXeUBr7osSCJNgvavWbM/06niWrOvYX2xwWdhXmXSrbX8ZbabVohBK41 email@example.com"
}

# EC2Instances
resource "aws_instance" "this" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.medium"
  subnet_id     = aws_subnet.this.id
}

# EC2Images
resource "aws_ami_from_instance" "this" {
  name               = "nuke-ami"
  source_instance_id = aws_instance.this.id
}

# EC2VPC
# EC2DefaultSecurityGroupRules
resource "aws_vpc" "this" {
  cidr_block = "10.0.0.0/16"
}

# EC2VPC
resource "aws_vpc" "this2" {
  cidr_block = "10.1.0.0/16"
}

# EC2Subnets
resource "aws_subnet" "this" {
  vpc_id            = aws_vpc.this.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "${var.region}a"
}

# EC2Subnets
resource "aws_subnet" "this2" {
  vpc_id            = aws_vpc.this.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "${var.region}b"
}

# EC2Subnets
resource "aws_subnet" "this3" {
  vpc_id            = aws_vpc.this.id
  cidr_block        = "10.0.3.0/24"
  availability_zone = "${var.region}c"
}

# EC2InternetGateways
# EC2InternetGatewayAttachmets
resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id
}

# EC2SecurityGroups
resource "aws_security_group" "this" {
  vpc_id = aws_vpc.this.id

  ingress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }
}

# EC2EIP
resource "aws_eip" "this" {
  vpc = true
}

# EC2VPCEndpoints
resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.this.id
  subnet_ids        = [aws_subnet.this.id]
  service_name      = "com.amazonaws.${var.region}.s3"
  vpc_endpoint_type = "Interface"
}

# EC2NetworkInterfaces
resource "aws_network_interface" "this" {
  subnet_id = aws_subnet.this.id
}

# EC2LaunchTemplates
resource "aws_launch_template" "this" {
  name = "nuke-launch-template"
  capacity_reservation_specification {
    capacity_reservation_preference = "open"
  }
  cpu_options {
    core_count       = 4
    threads_per_core = 2
  }
  image_id                             = data.aws_ami.ubuntu.id
  instance_initiated_shutdown_behavior = "terminate"
  instance_type                        = "t3.medium"
  network_interfaces {
    associate_public_ip_address = true
  }
  placement {
    availability_zone = "${var.region}a"
  }
}

# EC2Volumes
resource "aws_ebs_volume" "this" {
  availability_zone = "${var.region}a"
  size              = 10
}

# EC2Snapshots
resource "aws_ebs_snapshot" "this" {
  volume_id = aws_ebs_volume.this.id
}

# EC2NatGateways
resource "aws_nat_gateway" "this" {
  allocation_id = aws_eip.this.id
  subnet_id     = aws_subnet.this.id
  depends_on    = [aws_internet_gateway.this]
}

# EC2EgressOnlyInternetGateways
resource "aws_egress_only_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id
}

# EC2TransitGateways
resource "aws_ec2_transit_gateway" "this" {
  description = "this"
}

# EC2VPCPeeringConnections
resource "aws_vpc_peering_connection" "foo" {
  peer_vpc_id = aws_vpc.this.id
  vpc_id      = aws_vpc.this2.id
}

# EC2TransitGatewayAttachments
resource "aws_ec2_transit_gateway_vpc_attachment" "this" {
  subnet_ids         = [aws_subnet.this.id]
  transit_gateway_id = aws_ec2_transit_gateway.this.id
  vpc_id             = aws_vpc.this.id
}

# EC2NetworkAcls
resource "aws_network_acl" "this" {
  vpc_id = aws_vpc.this.id
}

# EC2CustomerGateways
resource "aws_customer_gateway" "this" {
  bgp_asn    = 65000
  ip_address = "172.83.124.10"
  type       = "ipsec.1"
}

# EC2VPCEndpointServiceConfigurations
resource "aws_vpc_endpoint_service" "this" {
  acceptance_required        = false
  network_load_balancer_arns = [aws_lb.network.arn]
}

# EC2VPCEndpoints
resource "aws_vpc_endpoint" "this" {
  vpc_id              = aws_vpc.this.id
  service_name        = aws_vpc_endpoint_service.this.service_name
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = false
}

# EC2VPCEndpointServiceConfigurations(Connections)
resource "aws_vpc_endpoint_connection_accepter" "this" {
  vpc_endpoint_service_id = aws_vpc_endpoint_service.this.id
  vpc_endpoint_id         = aws_vpc_endpoint.this.id
}

# ELBv2ELBs
resource "aws_lb" "network" {
  name               = "nuke-network-lb"
  internal           = true
  load_balancer_type = "network"
  subnets            = [aws_subnet.this.id]
}

# ELBv2TargetGroups
resource "aws_lb_target_group" "this" {
  name     = "nuke-lb-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.this.id
}

# EC2RouteTables
resource "aws_route_table" "this" {
  vpc_id = aws_vpc.this.id
  route {
    ipv6_cidr_block        = "::/0"
    egress_only_gateway_id = aws_egress_only_internet_gateway.this.id
  }
}
