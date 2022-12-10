from resources import resources
from resources.base import ResourceBase
from resources._types import ListResults, RemoveResults, FilterResults
from resources.utils import get_name_from_tags


class EC2InternetGatewayAttachmet(ResourceBase):
    def __init__(self, sess=None, default_filter_func=None) -> None:
        self.svc = sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func

    def list(self) -> ListResults:
        from .EC2VPC import EC2VPC

        results: list = []
        try:
            ec2_vpc = EC2VPC(self.svc, self.filter_func)
            vpcs, err = ec2_vpc.list(has_cache=True)
            if err:
                return results, err

            for vpc in vpcs:
                reason, err = ec2_vpc.filter(vpc)
                if err or reason:
                    continue

                vpc_id = vpc["id"]
                igws = self.svc.describe_internet_gateways(
                    Filters=[
                        {
                            "Name": "attachment.vpc-id",
                            "Values": [vpc_id],
                        }
                    ]
                )
                if not igws:
                    return results, None

                results += [
                    {
                        "id": igw["InternetGatewayId"],
                        "name": get_name_from_tags(igw.get("Tags", [])),
                        "state": igw["Attachments"][0]["State"],
                        "vpc_id": vpc_id,
                    }
                    for igw in igws["InternetGateways"]
                    if igw.get("Attachments")
                ]
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource) -> RemoveResults:
        try:
            self.svc.detach_internet_gateway(
                InternetGatewayId=resource["id"], VpcId=resource["vpc_id"]
            )
            return True, None
        except Exception as e:
            return False, e

    def filter(self, resource, *filters) -> FilterResults:
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
    resources.append(EC2InternetGatewayAttachmet)
