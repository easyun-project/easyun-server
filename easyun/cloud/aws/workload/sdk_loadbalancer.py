# -*- coding: utf-8 -*-
"""
  @module:  Load balancer SDK Module
  @desc:    AWS SDK Boto3 Loadbalancer(ELB v2) Client and Resource Wrapper.
  @auth:
"""

from botocore.exceptions import ClientError
from ..session import get_easyun_session


class LoadBalancer(object):
    def __init__(self, elb_id, dc_name=None):
        self.id = elb_id
        session = get_easyun_session(dc_name)
        self._client = session.client('elbv2')
        try:
            self.elbDict = self._client.describe_load_balancers(
                Names=[self.id]
            )['LoadBalancers'][0]
            self.arn = self.elbDict['LoadBalancerArn']
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_tags(self):
        try:
            elbTags = self._client.describe_tags(
                ResourceArns=[self.arn]
            )['TagDescriptions'][0].get('Tags')
            return elbTags
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_detail(self):
        elb = self.elbDict
        elbTags = self.get_tags()
        try:
            tagName = next(
                (tag['Value'] for tag in elbTags if tag["Key"] == 'Name'), None
            )
            userTags = [t for t in elbTags if t['Key'] not in ['Flag', 'Name']]
            elbBasic = {
                'elbId': elb['LoadBalancerName'],
                'tagName': tagName,
                'dnsName': elb['DNSName'],
                'elbType': elb['Type'],
                'elbState': elb['State']['Code'],
                'elbScheme': elb['Scheme']
            }
            elbListeners = [
            ]
            elbConfig = {}
            elbProperty = {}
            elbDetail = {
                'elbBasic': elbBasic,
                'elbListeners': elbListeners,
                'elbConfig': elbConfig,
                'elbProperty': elbProperty,
                'userTags': userTags,
            }
            return elbDetail
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def delete(self):
        elb = self.elbDict
        try:
            if elb['State'] != 'deleted':
                self._client.delete_load_balancer(
                    LoadBalancerArn=self.arn
                )
            else:
                raise ValueError('The Load Balancer was deleted!')
            oprtRes = {
                'operation': 'Delete Load Balancer',
                'natgwId': self.id,
                'tagName': self.tagName,
            }
            # del self
            return oprtRes
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))
