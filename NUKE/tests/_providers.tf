provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Project = "nuke"
    }
  }
}

provider "aws" {
  region = var.global_region
  alias  = "use1"

  default_tags {
    tags = {
      Project = "nuke"
    }
  }
}