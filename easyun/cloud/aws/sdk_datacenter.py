# -*- coding: utf-8 -*-
"""
  @module:  Datacenter SDK Module
  @desc:    AWS SDK Boto3 VPC Client and Resource Wrapper.
  @auth:    aleck
"""

from botocore.exceptions import ClientError
from easyun.common.models import Datacenter
from .sdk_subnet import Subnet
from .sdk_secgroup import SecurityGroup
from .sdk_staticip import StaticIP
from .sdk_gateway import InternetGateway, NatGateway
from ..utils import get_easyun_session, get_subnet_type, get_eni_type, get_tag_name


class DataCenter(object):
    def __init__(self, dcName):
        session = get_easyun_session(dcName)
        thisDC: Datacenter = Datacenter.query.filter_by(name=dcName).first()
        self.dcName = dcName
        self._resource = session.resource('ec2')
        self._client = self._resource.meta.client
        self.vpc = self._resource.Vpc(thisDC.vpc_id)
        self.tagFilter = {'Name': 'tag:Flag', 'Values': [dcName]}
        self.flagTag = {'Key': 'Flag', "Value": dcName}

    def get_azone_list(self):
        try:
            azs = self._client.describe_availability_zones()
            azoneList = [az['ZoneName'] for az in azs['AvailabilityZones']]
            return azoneList
        except Exception as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def list_all_subnet(self):
        try:
            subnets = self._client.describe_subnets(Filters=[self.tagFilter]).get(
                'Subnets'
            )

            subnetList = []
            for subnet in subnets:
                # 获取Tag:Name
                nameTag = next(
                    (
                        tag['Value']
                        for tag in subnet.get('Tags')
                        if tag["Key"] == 'Name'
                    ),
                    None,
                )
                # 判断subnet type是 public 还是 private
                subnetType = get_subnet_type(subnet['SubnetId'])
                subnet_record = {
                    'subnetId': subnet['SubnetId'],
                    'tagName': nameTag,
                    'subnetType': subnetType,
                    'subnetState': subnet['State'],
                    'vpcId': subnet['VpcId'],
                    'subnetAz': subnet['AvailabilityZone'],
                    'cidrBlock': subnet['CidrBlock'],
                    # 'cidrBlockv6':subnet['Ipv6CidrBlockAssociationSet'][0].get('Ipv6CidrBlock'),
                    'availableIpNum': subnet['AvailableIpAddressCount'],
                    'isMapPublicIp': subnet['MapPublicIpOnLaunch'],
                }
                subnetList.append(subnet_record)
            return subnetList
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_subnet_list(self):
        try:
            return self.list_all_subnet()
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def list_all_staticip(self):
        try:
            eips = self._client.describe_addresses(Filters=[self.tagFilter]).get(
                'Addresses'
            )

            eipList = []
            for eip in eips:
                nameTag = next(
                    (tag['Value'] for tag in eip.get('Tags') if tag['Key'] == 'Name'),
                    None,
                )
                eniType = get_eni_type(eip.get('NetworkInterfaceId'))
                eipItem = {
                    'pubIp': eip['PublicIp'],
                    'tagName': nameTag,
                    'alloId': eip['AllocationId'],
                    'eipDomain': eip['Domain'],
                    'ipv4Pool': eip['PublicIpv4Pool'],
                    'boarderGroup': eip['NetworkBorderGroup'],
                    'assoId': eip.get('AssociationId'),
                    # eip关联的目标ID及Name
                    'assoTarget': {
                        'svrId': eip.get('InstanceId'),
                        'tagName': get_tag_name('server', eip.get('InstanceId'))
                        if eniType == 'interface'
                        else get_tag_name('natgw', ''),
                        'eniId': eip.get('NetworkInterfaceId'),
                        'eniType': get_eni_type(eip.get('NetworkInterfaceId')),
                    },
                }
                eipList.append(eipItem)
            return eipList
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_staticip_list(self):
        try:
            eips = self._client.describe_addresses(Filters=[self.tagFilter]).get(
                'Addresses'
            )

            eipList = []
            for eip in eips:
                nameTag = next(
                    (tag['Value'] for tag in eip.get('Tags') if tag['Key'] == 'Name'), None,
                )
                eipItem = {
                    'publicIp': eip['PublicIp'],
                    'allocationId': eip['AllocationId'],
                    'tagName': nameTag,
                    # 可基于AssociationId判断eip是否可用
                    'associationId': eip.get('AssociationId'),
                    'isAvailable': True if not eip.get('AssociationId') else False,
                }
                eipList.append(eipItem)
            return eipList
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def list_all_secgroup(self):
        try:
            secGroups = self._client.describe_security_groups(
                Filters=[self.tagFilter]
            ).get('SecurityGroups')

            secgroupList = []
            for sg in secGroups:
                # 获取Tag:Name
                nameTag = next(
                    (tag['Value'] for tag in sg.get('Tags') if tag["Key"] == 'Name'), None,
                )
                sgItem = {
                    'sgId': sg['GroupId'],
                    'tagName': nameTag,
                    'sgName': sg['GroupName'],
                    'sgDesc': sg['Description'],
                    # Inbound Ip Permissions
                    'ibRulesNum': len(sg['IpPermissions']),
                    'ibPermissions': sg['IpPermissions'],
                    # Outbound Ip Permissions
                    'obRulesNum': len(sg['IpPermissionsEgress']),
                    'obPermissions': sg['IpPermissionsEgress'],
                }
                secgroupList.append(sgItem)
            return secgroupList
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_secgroup_list(self):
        try:
            return self.list_all_secgroup()
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def list_all_intgateway(self):
        try:
            igws = self._client.describe_internet_gateways(Filters=[self.tagFilter]).get(
                'InternetGateways'
            )

            igwList = []
            for igw in igws:
                nameTag = next(
                    (tag['Value'] for tag in igw.get('Tags') if tag['Key'] == 'Name'), None,
                )
                # 暂时只考虑1个igw对应1个vpc情况
                igwAttach = igw.get('Attachments')[0]
                igwItem = {
                    'igwId': igw['InternetGatewayId'],
                    'tagName': nameTag,
                    'vpcId': igwAttach['VpcId'],
                    'state': igwAttach['State'],
                }
            igwList.append(igwItem)
            return igwList
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def list_all_natgateway(self):
        try:
            natgws = self._client.describe_nat_gateways(Filters=[self.tagFilter]).get(
                'NatGateways'
            )
            natList = []
            for nat in natgws:
                nameTag = next(
                    (tag['Value'] for tag in nat.get('Tags') if tag['Key'] == 'Name'), None,
                )
                # 暂时只考虑1个natgw对应1个ip情况
                natAddr = nat['NatGatewayAddresses'][0]
                natItem = {
                    'natgwId': nat['NatGatewayId'],
                    'tagName': nameTag,
                    'subnetId': nat['SubnetId'],
                    'vpcId': nat['VpcId'],
                    'state': nat['State'],
                    'createTime': nat['CreateTime'],
                    'connectType': nat['ConnectivityType'],
                    'network': {
                        'publicIp': natAddr['PublicIp'],
                        'allocationId': natAddr['AllocationId'],
                        'privateIp': natAddr['PrivateIp'],
                        'eniId': natAddr['NetworkInterfaceId']
                    }
                }
            natList.append(natItem)
            return natList
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def list_all_routetable(self):
        try:
            rtbs = self._client.describe_route_tables(Filters=[self.tagFilter]).get(
                'RouteTables'
            )

            rtbList = []
            for rtb in rtbs:
                nameTag = next(
                    (tag['Value'] for tag in rtb.get('Tags') if tag['Key'] == 'Name'),
                    None,
                )
                rtbItem = {
                    'rtbId': rtb['RouteTableId'],
                    'tagName': nameTag,
                    'vpcId': rtb.get('VpcId'),
                    'rtbAssociations': rtb.get('Associations'),
                    'propagateVgws': rtb.get('PropagatingVgws'),
                    'rtbRoutes': rtb.get('Routes'),
                }
                rtbList.append(rtbItem)

            return rtbList
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def count_dc_resource(self, collection='all'):
        '''
        the VPC's available collections
          subnets, route_tables, internet_gateways,
          security_groups, network_acls,
          instances, network_interfaces,
          requested_vpc_peering_connections,
          accepted_vpc_peering_connections
        '''
        try:
            if collection == 'subnet':
                resIterator = self.vpc.route_tables.all()
            elif collection == 'rtb':
                resIterator = self.vpc.route_tables.all()
            elif collection == 'igw':
                resIterator = self.vpc.internet_gateways.all()
            elif collection == 'secgroup':
                resIterator = self.vpc.security_groups.all()
            elif collection == 'nacl':
                resIterator = self.vpc.network_acls.all()
            else:
                raise ValueError('bad collection name')

            rtbSum = 0
            for r in resIterator:
                flagValue = next(
                    (tag['Value'] for tag in r.tags if tag['Key'] == 'Flag'), None
                )
                if flagValue == self.dcName:
                    rtbSum += 1
            return rtbSum
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def create_secgroup(self, sg_name, sg_desc, tag_name=None):
        nameTag = {"Key": "Name", "Value": tag_name}
        try:
            newSg = self.vpc.create_security_group(
                GroupName=sg_name,
                Description=sg_desc,
                TagSpecifications=[{'ResourceType': 'security-group', "Tags": [self.flagTag, nameTag]}],
            )
            return SecurityGroup(self.dcName, newSg.id)
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def create_int_gateway(self, tag_name=None):
        nameTag = {"Key": "Name", "Value": tag_name}
        try:
            newIgw = self._resource.create_internet_gateway(
                TagSpecifications=[
                    {'ResourceType': 'internet-gateway', "Tags": [self.flagTag, nameTag]}
                ],
            )
            return InternetGateway(self.dcName, newIgw.id)
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def create_nat_gateway(self, connect_type, subnet_id, allocation_id, tag_name=None):
        nameTag = {"Key": "Name", "Value": tag_name}
        try:
            # 后续传 public_ip 转换 allocation_id
            newNat = self._client.create_nat_gateway(
                ConnectivityType=connect_type,
                AllocationId=allocation_id,
                SubnetId=subnet_id,
                TagSpecifications=[
                    {'ResourceType': 'natgateway', "Tags": [self.flagTag, nameTag]}
                ],
            )
            return NatGateway(self.dcName, newNat['NatGateway']['NatGatewayId'])
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))
