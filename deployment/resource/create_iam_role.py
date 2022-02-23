"""
  @module:  Easyun Deployment - IAM Role
  @desc:    Create IAM role for Easyun
  @auth:    aleck
"""
import boto3
import json 


Deploy_Region = 'us-east-1'


client_iam = boto3.client('iam', region_name= Deploy_Region)

def iam_role_creator(service, name):
    # service = ec2 | ecs | lambda 
    # name = 'easyun-service-control-role' | 'easyun-inventory-role'
    response = client_iam.create_role(
        # Path = "/",
        RoleName=name,
        AssumeRolePolicyDocument={
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": service+".amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        },
        Tags=[
            { 'Key': 'Flag', 'Value': 'EasyunDeploy' },
        ]
    )
    return response


def iam_policy_attach(role, policy):    
    response = client_iam.attach_role_policy(
        RoleName=role,
        PolicyArn=policy
    )
    return response

def iam_policy_creator(policy_list, name):
    response = client_iam.create_policy(
        PolicyName=name,
        PolicyDocument=json.dumps(policy_list),
        Description='string',
        Tags=[
            { 'Key': 'Flag', 'Value': 'EasyunDeploy' },
        ]
    )
    return response



easyun_service_control_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "servicequotas:ListServices",
                "iam:GenerateCredentialReport",
                "pricing:DescribeServices",
                "iam:List*",
                "iam:GenerateServiceLastAccessedDetails",
                "cloudformation:*",
                "servicequotas:GetRequestedServiceQuotaChange",
                "servicequotas:ListTagsForResource",
                "servicequotas:GetServiceQuota",
                "servicequotas:GetAssociationForServiceQuotaTemplate",
                "servicequotas:ListAWSDefaultServiceQuotas",
                "pricing:GetProducts",
                "servicequotas:GetServiceQuotaIncreaseRequestFromTemplate",
                "iam:Get*",
                "pricing:GetAttributeValues",
                "iam:SimulatePrincipalPolicy",
                "iam:SimulateCustomPolicy",
                "servicequotas:ListServiceQuotaIncreaseRequestsInTemplate",
                "servicequotas:ListRequestedServiceQuotaChangeHistory",
                "servicequotas:ListRequestedServiceQuotaChangeHistoryByQuota",
                "ce:*",
                "servicequotas:ListServiceQuotas",
                "servicequotas:GetAWSDefaultServiceQuota"
            ],
            "Resource": "*"
        }
    ]
}

easyun_dashboard_read_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "autoscaling:Describe*",
                "ec2:Describe*",
                "elasticloadbalancing:Describe*",
                "cloudwatch:GetMetricStatistics",
                "cloudwatch:Describe*",
                "cloudwatch:ListMetrics"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeAccountAttributes",
                "ec2:DescribeAddresses",
                "ec2:DescribeCarrierGateways",
                "ec2:DescribeClassicLinkInstances",
                "ec2:DescribeCustomerGateways",
                "ec2:DescribeDhcpOptions",
                "ec2:DescribeEgressOnlyInternetGateways",
                "ec2:DescribeFlowLogs",
                "ec2:DescribeInternetGateways",
                "ec2:DescribeLocalGatewayRouteTables",
                "ec2:DescribeLocalGatewayRouteTableVpcAssociations",
                "ec2:DescribeMovingAddresses",
                "ec2:DescribeNatGateways",
                "ec2:DescribeNetworkAcls",
                "ec2:DescribeNetworkInterfaceAttribute",
                "ec2:DescribeNetworkInterfacePermissions",
                "ec2:DescribeNetworkInterfaces",
                "ec2:DescribePrefixLists",
                "ec2:DescribeRouteTables",
                "ec2:DescribeSecurityGroupReferences",
                "ec2:DescribeSecurityGroupRules",
                "ec2:DescribeSecurityGroups",
                "ec2:DescribeStaleSecurityGroups",
                "ec2:DescribeSubnets",
                "ec2:DescribeTags",
                "ec2:DescribeVpcAttribute",
                "ec2:DescribeVpcClassicLink",
                "ec2:DescribeVpcClassicLinkDnsSupport",
                "ec2:DescribeVpcEndpoints",
                "ec2:DescribeVpcEndpointConnectionNotifications",
                "ec2:DescribeVpcEndpointConnections",
                "ec2:DescribeVpcEndpointServiceConfigurations",
                "ec2:DescribeVpcEndpointServicePermissions",
                "ec2:DescribeVpcEndpointServices",
                "ec2:DescribeVpcPeeringConnections",
                "ec2:DescribeVpcs",
                "ec2:DescribeVpnConnections",
                "ec2:DescribeVpnGateways"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:Get*",
                "s3:List*",
                "s3-object-lambda:Get*",
                "s3-object-lambda:List*"
            ],
            "Resource": "*"
        },
        {
            "Action": [
                "rds:Describe*",
                "rds:ListTagsForResource",
                "ec2:DescribeAccountAttributes",
                "ec2:DescribeAvailabilityZones",
                "ec2:DescribeInternetGateways",
                "ec2:DescribeSecurityGroups",
                "ec2:DescribeSubnets",
                "ec2:DescribeVpcAttribute",
                "ec2:DescribeVpcs"
            ],
            "Effect": "Allow",
            "Resource": "*"
        },
        {
            "Action": [
                "cloudwatch:GetMetricStatistics",
                "logs:DescribeLogStreams",
                "logs:GetLogEvents"
            ],
            "Effect": "Allow",
            "Resource": "*"
        }
    ]
}

