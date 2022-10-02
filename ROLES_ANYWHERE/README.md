# ROLES_ANYWHERE (In working)

[AWS IAM Roles Anywhere 적용하기](https://medium.com/@7424069/aws-iam-roles-anywhere-%EC%A0%81%EC%9A%A9%ED%95%98%EA%B8%B0-5f6db32e52f6)

## Cautions

1. ~~It's not complete because "rolesanywhere" resource has bugs. If you wanna know about these bugs then, refer to this [link](https://github.com/hashicorp/terraform-provider-aws/issues/26872).~~

- Congrats! It will works well from v4.34.0!! refer to this [link](https://github.com/hashicorp/terraform-provider-aws/blob/main/CHANGELOG.md).

2. This is all about "self signed certificate". If you wanna use "ACM's CERTIFICATE" then, modify "root-ca.tf" and delete "certs.tf" files.

- At this time, You remove "tls" provider and resources.

3. ~~If you wanna use "VPC Endpoint" then, replace "aws:SourceIp" to "aws:VpcSourceIp".~~

- You can use these condition both.

- If you don't know the difference between these conditions, refer to these links.([aws:VpcSourceIp](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_condition-keys.html#condition-keys-vpcsourceip), [aws:SourceIp](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_condition-keys.html#condition-keys-sourceip)).

## References

- [Obtaining temporary security credentials from AWS Identity and Access Management Roles Anywhere](https://docs.aws.amazon.com/rolesanywhere/latest/userguide/credential-helper.html)
