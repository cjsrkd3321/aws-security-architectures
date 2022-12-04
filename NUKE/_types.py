from typing import Literal

Services = list[Literal["ec2"] | Literal["iam"] | Literal["s3"] | Literal["kms"]]
