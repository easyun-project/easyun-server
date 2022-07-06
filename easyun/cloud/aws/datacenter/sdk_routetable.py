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
    def __init__(self, rtb_id, dc_name=None):
        session = get_easyun_session(dc_name)
        self.id = rtb_id
        self._resource = session.resource('ec2')
        self._client = self._resource.meta.client
        try:
            self.rtbObj = self._resource.RouteTable(self.id)
            self.routes = self.rtbObj.routes
            self.tagName = next(
                (tag['Value'] for tag in self.rtbObj.tags if tag["Key"] == 'Name'), None
            )
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_detail(self):
        rtb = self.rtbObj
        try:
            userTags = [t for t in rtb.tags if t['Key'] not in ['Flag', 'Name']]
            rtbDetail = {
                'rtbId': rtb.group_id,
                'tagName': self.tagName,
                'rtbName': rtb.group_name,
                'rtbDesc': rtb.description,
                # Inbound Ip Permissions
                'ibRulesNum': len(rtb.ip_permissions),
                'ibPermissions': rtb.ip_permissions,
                # Outbound Ip Permissions
                'obRulesNum': len(rtb.ip_permissions_egress),
                'obPermissions': rtb.ip_permissions_egress,
                'userTags': userTags,
            }
            return rtbDetail
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def delete(self):
        rtb = self.rtbObj
        try:
            if rtb.group_name != 'default':
                rtb.delete()
            else:
                raise ValueError('Can Not Delete the default SecurityGroup!')
            oprtRes = {
                'operation': 'Delete SecurityGroup',
                'rtbId': self.id,
                'rtbName': self.rtbName,
                'tagName': self.tagName,
            }
            # del self
            return oprtRes
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))
