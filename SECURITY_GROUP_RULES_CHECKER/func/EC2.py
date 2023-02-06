class EC2:
    def __init__(self, ec2):
        self.ec2 = ec2

    def is_ingress_rule(self, sgr):
        if sgr["IsEgress"]:
            return False
        return True

    def get_private_ips_using_sg_id(self, sg_id, nis):
        pips = []
        for ni in nis:
            for sg in ni["Groups"]:
                if sg["GroupId"] == sg_id:
                    pips.append(f"{ni['PrivateIpAddress']}/32")
        return pips

    @staticmethod
    def get_tag_value(tags, key):
        for tag in tags:
            if tag["Key"] == key:
                return tag["Value"]
        return None

    @property
    def network_interfaces(self):
        nis = self.ec2.describe_network_interfaces()["NetworkInterfaces"]
        return tuple([ni for ni in nis])

    @property
    def security_group_rules(self):
        iterator = self.ec2.get_paginator("describe_security_group_rules").paginate()
        return tuple([sgr for sgrs in iterator for sgr in sgrs["SecurityGroupRules"]])
