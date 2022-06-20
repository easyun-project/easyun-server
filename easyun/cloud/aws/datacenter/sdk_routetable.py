# -*- coding: utf-8 -*-
"""
  @module:  Route and Route Table SDK Module
  @desc:    AWS SDK Boto3 Route Table Client and Resource Wrapper.
  @auth:    aleck
"""

from botocore.exceptions import ClientError
from ..utils import get_easyun_session


TagEasyunSecurityGroup = [
    {
        'ResourceType': 'security-group',
        "Tags": [
            {"Key": "Flag", "Value": "Easyun"},
            {"Key": "Name", "Value": 'securitygroup[name]'},
        ],
    }
]


class RouteTable(object):
    def __init__(self, sg_id, dc_name=None):
        session = get_easyun_session(dc_name)
        self.id = sg_id
        self._resource = session.resource('ec2')
        self._client = self._resource.meta.client
        try:
            self.sgObj = self._resource.SecurityGroup(self.id)
            self.sgName = self.sgObj.group_name
            self.tagName = next(
                (tag['Value'] for tag in self.sgObj.tags if tag["Key"] == 'Name'), None
            )
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_detail(self):
        sg = self.sgObj
        try:
            userTags = [t for t in sg.tags if t['Key'] not in ['Flag', 'Name']]
            sgDetail = {
                'sgId': sg.group_id,
                'tagName': self.tagName,
                'sgName': sg.group_name,
                'sgDesc': sg.description,
                # Inbound Ip Permissions
                'ibRulesNum': len(sg.ip_permissions),
                'ibPermissions': sg.ip_permissions,
                # Outbound Ip Permissions
                'obRulesNum': len(sg.ip_permissions_egress),
                'obPermissions': sg.ip_permissions_egress,
                'userTags': userTags,
            }
            return sgDetail
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def delete(self):
        sg = self.sgObj
        try:
            if sg.group_name != 'default':
                sg.delete()
            else:
                raise ValueError('Can Not Delete the default SecurityGroup!')
            oprtRes = {
                'operation': 'Delete SecurityGroup',
                'sgId': self.id,
                'sgName': self.sgName,
                'tagName': self.tagName,
            }
            # del self
            return oprtRes
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))
