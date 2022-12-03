from ._base import ResourceBase
from . import resources, Config

import boto3


class EC2LaunchTemplate(ResourceBase):
    def __init__(self, region="ap-northeast-2", default_filter_func=None):
        self.svc = boto3.client("ec2", config=Config(region_name=region))
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func
        self.region = region

    def list(self):
        results = []
        try:
            iterator = self.svc.get_paginator("describe_launch_templates").paginate()
            results += [
                {
                    "id": template["LaunchTemplateName"],
                    "name": template["LaunchTemplateName"],
                    "tags": template.get("Tags", []),
                    "create_date": template["CreateTime"],
                    "unique_id": template["LaunchTemplateId"],
                }
                for templates in iterator
                for template in templates["LaunchTemplates"]
            ]
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource):
        try:
            return (
                self.svc.delete_launch_template(LaunchTemplateName=resource["id"])[
                    "ResponseMetadata"
                ]["HTTPStatusCode"]
                == 200
            ), None
        except Exception as e:
            return False, e

    def filter(self, resource, *filters):
        if self.filter_func:
            try:
                if self.filter_func(resource):
                    return self.filter_func.__name__, None
            except Exception as e:
                return False, e
        for filter in filters:
            if filter(resource):
                return filter.__name__, None
        return False, None

    def properties(self):
        pass


if __name__ != "__main__":
    resources.append(EC2LaunchTemplate)
