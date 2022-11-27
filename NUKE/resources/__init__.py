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
from .IAMUserAccessKeys import IAMUserAccessKey
from .IAMMfaDevices import IAMMfaDevice
from .IAMUserSshKeys import IAMUserSshKey
from .IAMSigningCertificates import IAMSigningCertificate
from .IAMServiceSpecificCredentials import IAMServiceSpecificCredential
from .IAMServerCertificates import IAMServerCertificate
from .IAMUserPolicyAttachments import IAMUserPolicyAttachment
from .IAMUserPolicies import IAMUserPolicy
from .IAMListUserGroupAttachments import IAMListUserGroupAttachment
from .IAMUsers import IAMUser

from IAMRolePolicies import IAMRolePolicy
from IAMRolePolicyAttachments import IAMRolePolicyAttachment
from .IAMRoles import IAMRole
