# -*- coding: utf-8 -*-
"""
  @module:  Datacenter SDK Module
  @desc:    AWS SDK Boto3 VPC Client and Resource Wrapper.
  @auth:    aleck
"""

from botocore.exceptions import ClientError
from easyun.common.models import Datacenter
from easyun.libs.utils import len_iter
from ..utils import get_easyun_session
from .sdk_subnet import Subnet
from .sdk_routetable import RouteTable
from .sdk_secgroup import SecurityGroup
from .sdk_staticip import StaticIP
from .sdk_gateway import InternetGateway, NatGateway
from ..workload import Workload
from ..resources import Resources
from ..sdk_tagging import ResGroupTagging
from ..utils import get_subnet_type, get_eni_type, get_tag_name


class DataCenter(object):
    def __init__(self, dc_name):
        thisDC: Datacenter = Datacenter.query.filter_by(name=dc_name).first()
        self._session = get_easyun_session(dc_name)
        self._resource = self._session.resource('ec2')
        self._client = self._resource.meta.client
        self.dcName = dc_name
        self.vpcId = thisDC.vpc_id
        self.vpc = self._resource.Vpc(self.vpcId)
        self.tagFilter = {'Name': 'tag:Flag', 'Values': [dc_name]}
        self.flagTag = {'Key': 'Flag', "Value": dc_name}
        self.workload = Workload(dc_name)
        self.tagging = ResGroupTagging(dc_name)
        self.resources = Resources(dc_name)

    def get_azone_list(self):
        try:
            azs = self._client.describe_availability_zones(
                Filters=[{'Name': 'state', 'Values': ['available']}]
            )['AvailabilityZones']
            azoneList = [az['ZoneName'] for az in azs]
            return azoneList
        except Exception as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def count_resource(self, resource='all'):
        '''
        the VPC's available collections
            subnet:     subnets,
            rtb:        route_tables,
            igw:        internet_gateways,
            natgw:      nat_gateways,
            secgroup:   security_groups,
            nacl:       network_acls,
            eni:        network_interfaces,
            instances, requested_vpc_peering_connections, accepted_vpc_peering_connections
        '''
        try:
            if resource == 'subnet':
                resIterator = self.vpc.subnets.all()
            elif resource == 'rtb':
                resIterator = self.vpc.route_tables.all()
            elif resource == 'igw':
                resIterator = self.vpc.internet_gateways.filter(
                    Filters=[self.tagFilter]
                )
            elif resource == 'natgw':
                natgws = self._client.describe_nat_gateways(
                    Filters=[self.tagFilter]
                ).get('NatGateways')
                return len(natgws)
            elif resource == 'secgroup':
                resIterator = self.vpc.security_groups.filter(Filters=[self.tagFilter])
            elif resource == 'nacl':
                resIterator = self.vpc.network_acls.filter(Filters=[self.tagFilter])
            elif resource == 'staticip':
                resIterator = self._resource.vpc_addresses.filter(
                    Filters=[self.tagFilter]
                )
            else:
                raise ValueError('bad collection name')
            # resSum = 0
            # for r in resIterator:
            #     flagValue = next(
            #         (tag['Value'] for tag in r.tags if tag['Key'] == 'Flag'), None
            #     )
            #     if flagValue == self.dcName:
            #         resSum += 1
            resNum = len_iter(resIterator)
            return resNum
        except ClientError as ex:
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
                    'azName': subnet['AvailabilityZone'],
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
                assoTarget = {}
                if eip.get('AssociationId'):
                    assoTarget = {
                        'svrId': eip.get('InstanceId'),
                        'tagName': get_tag_name('server', eip.get('InstanceId'))
                        if eniType == 'interface'
                        else get_tag_name('natgw', ''),
                        'eniId': eip.get('NetworkInterfaceId'),
                        'eniType': get_eni_type(eip.get('NetworkInterfaceId')),
                    }
                eipItem = {
                    'eipId': eip['AllocationId'],
                    'publicIp': eip['PublicIp'],
                    'tagName': nameTag,
                    'eipDomain': eip['Domain'],
                    'ipv4Pool': eip['PublicIpv4Pool'],
                    'boarderGroup': eip['NetworkBorderGroup'],
                    'associationId': eip.get('AssociationId'),
                    # eip关联的目标ID及Name
                    'assoTarget': assoTarget,
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
                    (tag['Value'] for tag in eip.get('Tags') if tag['Key'] == 'Name'),
                    None,
                )
                eipItem = {
                    'publicIp': eip['PublicIp'],
                    'eipId': eip['AllocationId'],
                    'tagName': nameTag,
                    # 可基于AssociationId判断eip是否可用
                    'associationId': eip.get('AssociationId'),
                    'isAvailable': False if eip.get('AssociationId') else True,
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
                    (tag['Value'] for tag in sg.get('Tags') if tag["Key"] == 'Name'),
                    None,
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
            igws = self._client.describe_internet_gateways(
                Filters=[self.tagFilter]
            ).get('InternetGateways')

            igwList = []
            for igw in igws:
                nameTag = next(
                    (tag['Value'] for tag in igw.get('Tags') if tag['Key'] == 'Name'),
                    None,
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
                    (tag['Value'] for tag in nat.get('Tags') if tag['Key'] == 'Name'),
                    None,
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
                        'eniId': natAddr['NetworkInterfaceId'],
                    },
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
                    'associations': rtb.get('Associations'),
                    'propagateVgws': rtb.get('PropagatingVgws'),
                    'routes': rtb.get('Routes'),
                }
                rtbList.append(rtbItem)

            return rtbList
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def create_subnet(self, cidr_block, az_name, tag_name=None):
        nameTag = {"Key": "Name", "Value": tag_name}
        try:
            newSubnet = self.vpc.create_subnet(
                CidrBlock=cidr_block,
                AvailabilityZone=az_name,
                TagSpecifications=[
                    {'ResourceType': 'subnet', "Tags": [self.flagTag, nameTag]}
                ],
            )
            return Subnet(newSubnet.id, self.dcName)
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def create_routetable(self, tag_name=None):
        nameTag = {"Key": "Name", "Value": tag_name}
        try:
            newRtb = self.vpc.create_route_table(
                TagSpecifications=[
                    {'ResourceType': 'route-table', "Tags": [self.flagTag, nameTag]}
                ],
            )
            return RouteTable(newRtb.id, self.dcName)
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def create_secgroup(self, sg_name, sg_desc, tag_name=None):
        nameTag = {"Key": "Name", "Value": tag_name}
        try:
            newSg = self.vpc.create_security_group(
                GroupName=sg_name,
                Description=sg_desc,
                TagSpecifications=[
                    {'ResourceType': 'security-group', "Tags": [self.flagTag, nameTag]}
                ],
            )
            return SecurityGroup(newSg.id, self.dcName)
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def create_staticip(self, tag_name=None):
        if tag_name:
            nameTag = {"Key": "Name", "Value": tag_name}
        else:
            nameTag = {"Key": "Name", "Value": self.dcName.lower() + "-static-ip"}
        try:
            newEip = self._client.allocate_address(
                Domain='vpc',
                TagSpecifications=[
                    {'ResourceType': 'elastic-ip', "Tags": [self.flagTag, nameTag]}
                ],
            )
            return StaticIP(newEip['AllocationId'], self.dcName)
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def create_int_gateway(self, tag_name=None):
        nameTag = {"Key": "Name", "Value": tag_name}
        try:
            newIgw = self._resource.create_internet_gateway(
                TagSpecifications=[
                    {
                        'ResourceType': 'internet-gateway',
                        "Tags": [self.flagTag, nameTag],
                    }
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
