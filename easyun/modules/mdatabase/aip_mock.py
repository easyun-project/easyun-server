# -*- coding: utf-8 -*-
"""
  @module:  Database Mock API
  @desc:    put database module's mock api code here.
  @auth:    
"""

import boto3
from apiflask import Schema, input, output, auth_required
from apiflask.fields import Integer, String, List, Dict
from apiflask.validators import Length, OneOf
from easyun.common.result import Result
from easyun.cloud.utils import query_dc_list
from datetime import date, datetime
from . import bp



# .describe_db_instances() 
resp = [
    {
        'DBInstanceIdentifier': 'database-1-reader',
        'DBInstanceClass': 'db.t3.small',
        'Engine': 'aurora-mysql',
        'DBInstanceStatus': 'available',
        'MasterUsername': 'admin',
        'Endpoint': {
            'Address': 'database-1-reader.cdtqu9lrfh05.us-east-1.rds.amazonaws.com',
            'Port': 3306,
            'HostedZoneId': 'Z2R2ITUGPM61AM'
    },
    'AllocatedStorage': 1,
    # 'InstanceCreateTime': datetime.datetime(2022, 1, 16, 9, 59, 45, 116000, tzinfo=tzlocal()),
    'PreferredBackupWindow': '08:50-09:20',
    'BackupRetentionPeriod': 1,
    'DBSecurityGroups': [],
    'VpcSecurityGroups': [{'VpcSecurityGroupId': 'sg-05df5c8e8396d06e9',
    'Status': 'active'},
    {'VpcSecurityGroupId': 'sg-0a818f9a74c0657ad', 'Status': 'active'}],
    'DBParameterGroups': [{'DBParameterGroupName': 'default.aurora-mysql5.7',
    'ParameterApplyStatus': 'in-sync'}],
    'AvailabilityZone': 'us-east-1a',
    'DBSubnetGroup': {'DBSubnetGroupName': 'default-vpc-057f0e3d715c24147',
    'DBSubnetGroupDescription': 'Created from the RDS Management Console',
    'VpcId': 'vpc-057f0e3d715c24147',
    'SubnetGroupStatus': 'Complete',
    'Subnets': [{'SubnetIdentifier': 'subnet-02a09fd044f6d8e8d',
        'SubnetAvailabilityZone': {'Name': 'us-east-1b'},
        'SubnetOutpost': {},
        'SubnetStatus': 'Active'},
    {'SubnetIdentifier': 'subnet-0c903785974d075f0',
        'SubnetAvailabilityZone': {'Name': 'us-east-1b'},
        'SubnetOutpost': {},
        'SubnetStatus': 'Active'},
    {'SubnetIdentifier': 'subnet-03c3de7f09dfe36d7',
        'SubnetAvailabilityZone': {'Name': 'us-east-1a'},
        'SubnetOutpost': {},
        'SubnetStatus': 'Active'},
    {'SubnetIdentifier': 'subnet-06bfe659f6ecc2eed',
        'SubnetAvailabilityZone': {'Name': 'us-east-1a'},
        'SubnetOutpost': {},
        'SubnetStatus': 'Active'}]},
    'PreferredMaintenanceWindow': 'mon:04:25-mon:04:55',
    'PendingModifiedValues': {},
    'MultiAZ': False,
    'EngineVersion': '5.7.mysql_aurora.2.07.2',
    'AutoMinorVersionUpgrade': True,
    'ReadReplicaDBInstanceIdentifiers': [],
    'LicenseModel': 'general-public-license',
    'OptionGroupMemberships': [{'OptionGroupName': 'default:aurora-mysql-5-7',
    'Status': 'in-sync'}],
    'PubliclyAccessible': False,
    'StorageType': 'aurora',
    'DbInstancePort': 0,
    'DBClusterIdentifier': 'database-1',
    'StorageEncrypted': True,
    'KmsKeyId': 'arn:aws:kms:us-east-1:565521294060:key/a751f111-929e-4cf9-8de2-947fcf5afff1',
    'DbiResourceId': 'db-IIVRWE6S7G6XNMUTTAC3HMJ7KY',
    'CACertificateIdentifier': 'rds-ca-2019',
    'DomainMemberships': [],
    'CopyTagsToSnapshot': False,
    'MonitoringInterval': 0,
    'PromotionTier': 1,
    'DBInstanceArn': 'arn:aws:rds:us-east-1:565521294060:db:database-1-reader',
    'IAMDatabaseAuthenticationEnabled': False,
    'PerformanceInsightsEnabled': False,
    'DeletionProtection': False,
    'AssociatedRoles': [],
    'TagList': [],
    'CustomerOwnedIpEnabled': False},
]
