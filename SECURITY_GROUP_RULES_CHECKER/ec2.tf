resource "aws_instance" "this" {
  ami                    = data.aws_ami.this.id
  instance_type          = "t3.medium"
  subnet_id              = data.aws_subnets.this.ids[0]
  vpc_security_group_ids = [aws_security_group.this.id]

  user_data = <<-EOF
                  #!/bin/bash
                  sudo su
                  yum -y install httpd
                  echo "<p> My Instance! </p>" >> /var/www/html/index.html
                  sudo systemctl enable httpd
                  sudo systemctl start httpd
                  EOF
}

resource "aws_security_group" "this" {
  name   = "rex"
  vpc_id = aws_default_vpc.default.id
}

resource "aws_security_group_rule" "this" {
  type              = "ingress"
  from_port         = 80
  to_port           = 80
  protocol          = "tcp"
  cidr_blocks       = ["${trimspace(data.http.myip.response_body)}/32"]
  security_group_id = aws_security_group.this.id
}

resource "aws_security_group_rule" "ssh" {
  type              = "ingress"
  from_port         = 22
  to_port           = 22
  protocol          = "tcp"
  cidr_blocks       = ["${trimspace(data.http.myip.response_body)}/32"]
  security_group_id = aws_security_group.this.id
}

resource "aws_security_group_rule" "this2" {
  type              = "egress"
  from_port         = 0
  to_port           = 65535
  protocol          = "all"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.this.id
}

resource "null_resource" "this" {
  provisioner "local-exec" {
    command = "while true; do curl http://${aws_instance.this.public_dns}; sleep 2; done;"
  }
}