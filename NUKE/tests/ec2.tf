resource "aws_key_pair" "this" {
  key_name   = "deployer-key"
  public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQD3F6tyPEFEzV0LX3X8BsXdMsQz1x2cEikKDEY0aIj41qgxMCP/iteneqXSIFZBp5vizPvaoIR3Um9xK7PGoW8giupGn+EPuxIA4cDM4vzOqOkiMPhz5XK0whEjkVzTo4+S0puvDZuwIsdiW9mxhJc7tgBNL0cYlWSYVkz4G/fslNfRPW5mYAM49f4fhtxPb5ok4Q2Lg9dPKVHO/Bgeu5woMc7RY0p1ej6D4CKFE6lymSDJpW0YHX/wqE9+cfEauh7xZcG0q9t2ta6F6fmX0agvpFyZo8aFbXeUBr7osSCJNgvavWbM/06niWrOvYX2xwWdhXmXSrbX8ZbabVohBK41 email@example.com"
}

# EC2Instances
resource "aws_instance" "this" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"
  subnet_id     = aws_subnet.this.id
}

# EC2Images
resource "aws_ami_from_instance" "this" {
  name               = "terraform-example"
  source_instance_id = aws_instance.this.id
}

# EC2VPC
# EC2DefaultSecurityGroupRules
resource "aws_vpc" "this" {
  cidr_block = "10.0.0.0/16"
}

# EC2Subnets
resource "aws_subnet" "this" {
  vpc_id     = aws_vpc.this.id
  cidr_block = "10.0.1.0/24"
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
  vpc_id       = aws_vpc.this.id
  service_name = "com.amazonaws.${var.region}.s3"
}

# EC2NetworkInterfaces
resource "aws_network_interface" "this" {
  subnet_id = aws_subnet.this.id
}