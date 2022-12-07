from resources import resources
from resources.base import ResourceBase


class EC2Image(ResourceBase):
    def __init__(self, sess=None, region="ap-northeast-2", default_filter_func=None):
        self.svc = sess[region]["ec2"] if type(sess) == dict else sess
        self.exceptions = self.svc.exceptions
        self.filter_func = default_filter_func
        self.region = region

    def list(self):
        results = []
        try:
            images = self.svc.describe_images(Owners=["self"])["Images"]
            for image in images:
                results.append(
                    {
                        "id": image["ImageId"],
                        "tags": image.get("Tags", []),
                        "name": image["Name"],
                        "state": image["State"],
                        "type": image["ImageType"],
                        "create_date": image["CreationDate"],
                        "architecture": image.get("Architecture"),
                        "platform": image.get("Platform"),
                    }
                )
            return results, None
        except Exception as e:
            return results, e

    def remove(self, resource):
        try:
            self.svc.deregister_image(ImageId=resource["id"])
            return True, None
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
    resources.append(EC2Image)
