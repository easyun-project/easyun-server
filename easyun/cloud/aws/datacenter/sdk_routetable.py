# -*- coding: utf-8 -*-
"""
  @module:  Route and Route Table SDK Module
  @desc:    AWS SDK Boto3 Route Table Client and Resource Wrapper.
  @auth:    aleck
"""

from botocore.exceptions import ClientError
from ..session import get_easyun_session


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
            routes = []
            for route in rtb.routes:
                routes.append({
                    'destinationCidr': route.destination_cidr_block,
                    'gatewayId': route.gateway_id,
                    'natGatewayId': route.nat_gateway_id,
                    'state': route.state,
                })
            associations = []
            for assoc in rtb.associations:
                associations.append({
                    'associationId': assoc.id,
                    'subnetId': assoc.subnet_id,
                    'main': assoc.main,
                })
            rtbDetail = {
                'rtbId': rtb.id,
                'tagName': self.tagName,
                'vpcId': rtb.vpc_id,
                'routes': routes,
                'associations': associations,
                'userTags': userTags,
            }
            return rtbDetail
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def delete(self):
        rtb = self.rtbObj
        try:
            # disassociate all non-main associations first
            for assoc in rtb.associations:
                if not assoc.main:
                    assoc.delete()
            rtb.delete()
            oprtRes = {
                'operation': 'Delete RouteTable',
                'rtbId': self.id,
                'tagName': self.tagName,
            }
            return oprtRes
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))
