from typing import List
from botocore.config import Config

# resources
resources: List = []

from .EC2Instances import EC2Instance
from .EC2NetworkInterfaceAttachmets import EC2NetworkInterfaceAttachmet
from .EC2NetworkInterfaces import EC2NetworkInterface
from .EC2SecurityGroups import EC2SecurityGroup
from .EC2InternetGatewayAttachmets import EC2InternetGatewayAttachmet
from .EC2InternetGateways import EC2InternetGateway
from .EC2Subnets import EC2Subnet
from .EC2VPC import EC2VPC

from .IAMLoginProfiles import IAMLoginProfile
from .IAMUserPolicies import IAMUserPolicy
from .IAMUserPolicyAttachments import IAMUserPolicyAttachment
from .IAMUserAccessKeys import IAMUserAccessKey
from .IAMVirtualMfaDevices import IAMVirtualMfaDevice

from .IAMUsers import IAMUser

# from .IAMRoles import IAMRole
