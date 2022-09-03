resource "aws_instance" "web" {
  ami           = "ami-05fa00d4c63e32376"
  instance_type = "t3.medium"

  tags = {
    Name = "HelloWorld"
  }
}