# -*- coding: utf-8 -*-
"""
  @module:  The API Wrapper Module
  @desc:    AWS SDK Boto3 ResourceGroups Tagging Client and Resource Wrapper.
  @auth:    aleck
"""
import boto3


ResourcesDict = {
    'vpc': 'ec2:vpc',
    'subnet': 'ec2:subnet',
    'natgw': 'ec2:natgateway',
    'igw': 'ec2:internet-gateway',
    'secgroup': 'ec2:security-group',
    'nwacl': 'ec2:network-acl',
    'rtb': 'ec2:route-table',
    'eip': 'ec2:elastic-ip',
    'nic': 'ec2:network-interface',
    'server': 'ec2:instance',
    'keypair': 'ec2:key-pair',
    'volume': 'ec2:volume',
    'bucket': 's3:bucket',
    'efs': 'elasticfilesystem:file-system',
    'fsx': 'fsx:file-system',
    'database': 'rds:db',
    'ddb': 'dynamodb:table',
    'elb': 'elasticloadbalancing:loadbalancer',
    'targetgroup': 'elasticloadbalancing:targetgroup',
    'volbackup': 'ec2:snapshot',
    'rdsbackup': 'rds:snapshot',
    'efsbackup': 'backup:recovery-point',
}


# SDK: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/resourcegroupstaggingapi.html
class ResGroupTagging(object):
    def __init__(self, dc_tag):
        self._client = boto3.client('resourcegroupstaggingapi')
        self.filterTag = {'Key': 'Flag', 'Values': [dc_tag]}

    # ResourceGroupsTaggingAPI.Client.get_resources
    def get_resources(self, resource):
        paginator = self._client.get_paginator('get_resources')
        res_iterator = paginator.paginate(
            # 'TARGET_ID'|'REGION'|'RESOURCE_TYPE',
            ResourceTypeFilters=[resource],
            TagFilters=[self.filterTag],
        )
        resList = [
            res for page in res_iterator for res in page['ResourceTagMappingList']
        ]

        return resList

    def sum_resources(self, resource):
        resSum = len(self.get_resources(resource))
        return resSum

    def get_resource_arn(self, resource):
        resList = self.get_resources(resource)
        arnList = [r['ResourceARN'] for r in resList]
        return arnList
