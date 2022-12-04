from typing import Literal, List

Services = List[
    Literal["ec2"]
    | Literal["iam"]
    | Literal["s3"]
    | Literal["kms"]
    | Literal["lambda"]
    | Literal["kafka"]
    | Literal["secretsmanager"]
    | Literal["ssm"]
]
