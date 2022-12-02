from botocore.config import Config

# resources
resources: list = []

from .EC2KeyPairs import EC2KeyPair
from .EC2Images import EC2Image
from .EC2EIP import EC2EIP
from .EC2VPCEndpoints import EC2VPCEndpoint
from .EC2DefaultSecurityGroupRules import EC2DefaultSecurityGroupRule
from .EC2Instances import EC2Instance
from .EC2NetworkInterfaces import EC2NetworkInterface
from .EC2SecurityGroups import EC2SecurityGroup
from .EC2InternetGatewayAttachmets import EC2InternetGatewayAttachmet
from .EC2InternetGateways import EC2InternetGateway
from .EC2Subnets import EC2Subnet
from .EC2VPC import EC2VPC

from .IAMUserPermissionsBoundaries import IAMUserPermissionsBoundary
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

from .IAMRolePolicies import IAMRolePolicy
from .IAMRolePolicyAttachments import IAMRolePolicyAttachment
from .IAMInstanceProfileRoles import IAMInstanceProfileRole
from .IAMInstanceProfiles import IAMInstanceProfile
from .IAMRoles import IAMRole

from .IAMPolicyVersions import IAMPolicyVersion
from .IAMPolicies import IAMPolicy

from .IAMGroupPolicyAttachments import IAMGroupPolicyAttachment
from .IAMGroupPolicies import IAMGroupPolicy
from .IAMGroups import IAMGroup
