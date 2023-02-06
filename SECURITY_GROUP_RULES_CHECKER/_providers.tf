provider "aws" {
  region = "ap-northeast-2"

  default_tags {
    tags = {
      Name  = "sg-valid"
      Owner = "rex.chun"
    }
  }
}