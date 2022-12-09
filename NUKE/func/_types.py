from typing import Literal, List, Union

Services = List[
    Union[
        Literal["ec2"],
        Literal["iam"],
        Literal["s3"],
        Literal["kms"],
        Literal["lambda"],
        Literal["kafka"],
        Literal["secretsmanager"],
        Literal["ssm"],
        Literal["logs"],
        Literal["sqs"],
        Literal["dynamodb"],
        Literal["rds"],
        Literal["sns"],
        Literal["grafana"],
        Literal["eks"],
        Literal["emr"],
        Literal["ecr"],
        Literal["efs"],
        Literal["acm"],
        Literal["acm-pca"],
    ]
]
