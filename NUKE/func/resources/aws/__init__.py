# EC2
from .EC2TransitGatewayAttachments import EC2TransitGatewayAttachment
from .EC2VPCPeeringConnections import EC2VPCPeeringConnection
from .EC2TransitGateways import EC2TransitGateway
from .EC2EgressOnlyInternetGateways import EC2EgressOnlyInternetGateway
from .EC2NatGateways import EC2NatGateway
from .EC2Volumes import EC2Volume
from .EC2Snapshots import EC2Snapshot
from .EC2LaunchTemplates import EC2LaunchTemplate
from .EC2KeyPairs import EC2KeyPair
from .EC2Images import EC2Image
from .EC2EIP import EC2EIP
from .EC2VPCEndpoints import EC2VPCEndpoint
from .EC2DefaultSecurityGroupRules import EC2DefaultSecurityGroupRule
from .EC2Instances import EC2Instance

# from .EC2NetworkInterfaces import EC2NetworkInterface
from .EC2SecurityGroups import EC2SecurityGroup
from .EC2InternetGatewayAttachmets import EC2InternetGatewayAttachmet
from .EC2InternetGateways import EC2InternetGateway
from .EC2Subnets import EC2Subnet
from .EC2VPC import EC2VPC

# IAM
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

from .IAMOpenIdConnectProviders import IAMOpenIdConnectProvider
from .IAMSamlProviders import IAMSamlProvider

# S3
from .S3Buckets import S3Bucket

# from .S3Objects import S3Object # If you wanna delete the specific object then, use it.

# KMS
from .KMSKeys import KMSKey

# LAMBDA
from .LAMBDAFunctions import LAMBDAFunction

# MSK
from .MSKClusters import MSKCluster

# SECRETSMANAGER
from .SECRETSMANAGERSecrets import SECRETSMANAGERSecret

# SSM
from .SSMParameters import SSMParameter

# CLOUDWATCH
from .CLOUDWATCHLOGSLogGroups import CLOUDWATCHLOGSLogGroup

# SQS
from .SQSQueues import SQSQueue

# DYNAMODB
from .DYNAMODBTables import DYNAMODBTable

# RDS
from .RDSClusters import RDSCluster
from .RDSClusterParameterGroups import RDSClusterParameterGroup
from .RDSDbParameterGroups import RDSDbParameterGroup
from .RDSSubnets import RDSSubnet
from .RDSInstances import RDSInstance
from .RDSEventSubscriptions import RDSEventSubscription

# SNS
from .SNSTopics import SNSTopic
