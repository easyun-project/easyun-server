# -*- coding: utf-8 -*-
"""
  @module:  Static IP SDK Module
  @desc:    AWS SDK Boto3 StaticIP(EIP) Client and Resource Wrapper.
  @auth:
"""

from botocore.exceptions import ClientError
from ..utils import get_easyun_session, get_eni_type, get_tag_name


class StaticIP(object):
    def __init__(self, eip_id, dc_name):
        session = get_easyun_session(dc_name)
        self.id = eip_id
        self._resource = session.resource('ec2')
        self._client = self._resource.meta.client
        try:
            self.eipObj = self._resource.VpcAddress(self.id)
            self.publicIp = self.eipObj.public_ip
            self.tagName = next(
                (tag['Value'] for tag in self.eipObj.tags if tag["Key"] == 'Name'), None
            )
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_detail(self):
        eip = self.eipObj
        try:
            userTags = [t for t in eip.tags if t['Key'] not in ['Flag', 'Name']]
            eniType = get_eni_type(eip.network_interface_id)
            eipBasic = {
                'eipId': eip.allocation_id,
                'publicIp': eip.public_ip,
                'tagName': self.tagName,
                'associationId': eip.association_id,
                # 基于AssociationId判断 eip是否可用
                'isAvailable': False if eip.get('AssociationId') else True                
            }
            eipDetail = {
                'eipBasic': eipBasic,
                'eipProperty': {
                    'eipDomain': eip.domain,
                    'ipv4Pool': eip.public_ipv4_pool,
                    'boarderGroup': eip.network_border_group,
                },
                # eip关联的目标ID及Name
                'assoTarget': {
                    'svrId': eip.instance_id,
                    'tagName': get_tag_name('server', eip.instance_id) if eniType == 'interface' else get_tag_name('natgw', ''),
                    'eniId': eip.network_interface_id,
                    'eniType': eniType,
                },
                'userTags': userTags
            }
            return eipDetail
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def delete(self):
        eip = self.eipObj
        try:
            eip.release()
            oprtRes = {
                'operation': 'Delete StaticIP',
                'eipId': self.id,
                'tagName': self.tagName,
            }
            # del self
            return oprtRes
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))
