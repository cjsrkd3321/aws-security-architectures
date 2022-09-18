resource "aws_instance" "web" {
  ami           = "ami-05fa00d4c63e32376"
  instance_type = "t3.medium"

  iam_instance_profile = aws_iam_instance_profile.profile.name

  tags = {
    Name = "HelloWorld"
  }
}

resource "aws_instance" "web2" {
  ami           = "ami-05fa00d4c63e32376"
  instance_type = "t3.medium"

  iam_instance_profile = aws_iam_instance_profile.profile.name

  tags = {
    Name = "HelloWorld2"
  }
}

resource "aws_instance" "web3" {
  provider = aws.apne2

  ami           = "ami-01d87646ef267ccd7"
  instance_type = "t3.medium"

  iam_instance_profile = aws_iam_instance_profile.profile.name

  tags = {
    Name = "HelloWorld3"
  }
}

resource "aws_instance" "web4" {
  provider = aws.use2

  ami           = "ami-0568773882d492fc8"
  instance_type = "t3.medium"

  iam_instance_profile = aws_iam_instance_profile.profile.name

  tags = {
    Name = "HelloWorld4"
  }
}