# -*- coding: utf-8 -*-
"""
  @module:  Datacenter SDK Module
  @desc:    AWS SDK Boto3 VPC Client and Resource Wrapper
"""

from botocore.exceptions import ClientError
from easyun.common.models import Datacenter
from easyun.libs.utils import len_iter
from .session import get_easyun_session
from .resource.network.sdk_subnet import Subnet
from .resource.network.sdk_routetable import RouteTable
from .resource.network.sdk_secgroup import SecurityGroup
from .resource.network.sdk_staticip import StaticIP
from .resource.network.sdk_gateway import InternetGateway, NatGateway
from .resource import Resource
from .resource.compute.sdk_server import EC2Server
from .resource.storage.sdk_volume import StorageVolume
from .resource.storage.sdk_bucket import StorageBucket
from .resource.database.sdk_database import DBInstance
from .resource.network.sdk_loadbalancer import LoadBalancer
from .management.sdk_tagging import ResGroupTagging
from .utils import get_subnet_type, get_eni_type, get_tag_name


class DataCenter(object):
    def __init__(self, dc_name):
        thisDC: Datacenter = Datacenter.query.filter_by(name=dc_name).first()
        self._session = get_easyun_session(dc_name)
        self._resource = self._session.resource('ec2')
        self._client = self._resource.meta.client
        self.dcName = dc_name
        self.vpcId = thisDC.vpc_id if thisDC else None
        self.vpc = self._resource.Vpc(self.vpcId) if self.vpcId else None
        self.tagFilter = {'Name': 'tag:Flag', 'Values': [dc_name]}
        self.flagTag = {'Key': 'Flag', "Value": dc_name}
        self.resource = Resource(dc_name)
        self.tagging = ResGroupTagging(dc_name)

    @classmethod
    def create(cls, name, region, account_id, user=None):
        """创建 DataCenter 逻辑容器（写 DB），返回实例"""
        from easyun import db
        from datetime import datetime
        dc_record = Datacenter(
            name=name, cloud='AWS', account_id=account_id,
            region=region, vpc_id=None,
            create_date=datetime.utcnow(), create_user=user,
        )
        db.session.add(dc_record)
        db.session.commit()
        return cls(name)

    # --- 资源获取 ---
    def get_subnet(self, subnet_id):
        return Subnet(subnet_id, self.dcName)

    def get_routetable(self, rtb_id):
        return RouteTable(rtb_id, self.dcName)

    def get_secgroup(self, sg_id):
        return SecurityGroup(sg_id, self.dcName)

    def get_int_gateway(self, igw_id):
        return InternetGateway(igw_id, self.dcName)

    def get_nat_gateway(self, natgw_id):
        return NatGateway(natgw_id, self.dcName)

    def get_staticip(self, eip_id):
        return StaticIP(eip_id, self.dcName)

    def get_server(self, svr_id):
        return EC2Server(svr_id, self.dcName)

    def get_volume(self, volume_id):
        return StorageVolume(volume_id, self.dcName)

    def get_disk_type(self, attach_path):
        return StorageVolume.get_disk_type(attach_path)

    def get_bucket(self, bucket_id):
        return StorageBucket(bucket_id, self.dcName)

    def validate_bucket_name(self, bucket_id):
        """检查 bucket 名称是否已存在"""
        from .resource.storage.sdk_bucket import vaildate_bucket_exist
        return vaildate_bucket_exist(bucket_id, self.dcName)

    def get_db_instance(self, dbi_id):
        return DBInstance(dbi_id, self.dcName)

    def get_load_balancer(self, elb_id):
        return LoadBalancer(elb_id, self.dcName)

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
            return InternetGateway(newIgw.id, self.dcName)
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
            return NatGateway(newNat['NatGateway']['NatGatewayId'], self.dcName)
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    # --- VPC 生命周期 ---

    def create_vpc(self, cidr_block):
        """创建 VPC 并绑定到当前 DataCenter"""
        from easyun import db
        vpc = self._resource.create_vpc(
            CidrBlock=cidr_block,
            TagSpecifications=[{'ResourceType': 'vpc', 'Tags': [self.flagTag, {'Key': 'Name', 'Value': 'VPC-' + self.dcName}]}],
        )
        vpc.wait_until_available()
        vpc.modify_attribute(EnableDnsSupport={'Value': True})
        vpc.modify_attribute(EnableDnsHostnames={'Value': True})
        # 更新 DB 和实例状态
        dc_record = Datacenter.query.filter_by(name=self.dcName).first()
        dc_record.vpc_id = vpc.id
        db.session.commit()
        self.vpcId = vpc.id
        self.vpc = vpc
        return vpc

    def attach_igw(self, igw_id):
        """将 IGW 关联到 VPC"""
        self.vpc.attach_internet_gateway(InternetGatewayId=igw_id)

    def add_route(self, route_table_id, dest_cidr, gateway_id=None, nat_gateway_id=None):
        """向路由表添加路由"""
        rt = self._resource.RouteTable(route_table_id)
        kwargs = {'DestinationCidrBlock': dest_cidr}
        if gateway_id:
            kwargs['GatewayId'] = gateway_id
        if nat_gateway_id:
            kwargs['NatGatewayId'] = nat_gateway_id
        rt.create_route(**kwargs)

    def associate_subnet_to_rtb(self, route_table_id, subnet_id):
        """将子网关联到路由表"""
        rt = self._resource.RouteTable(route_table_id)
        rt.associate_with_subnet(SubnetId=subnet_id)

    def delete_nat_gateways(self):
        """删除 VPC 下所有 NAT Gateway（等待完成）"""
        natgws = self._client.describe_nat_gateways(
            Filters=[{'Name': 'tag:Flag', 'Values': [self.dcName]}]
        ).get('NatGateways', [])
        ids = []
        for ng in natgws:
            if ng.get('State') != 'deleted':
                self._client.delete_nat_gateway(NatGatewayId=ng['NatGatewayId'])
                ids.append(ng['NatGatewayId'])
        if ids:
            self._client.get_waiter('nat_gateway_deleted').wait(NatGatewayIds=ids)
        return ids

    def delete_network_acls(self):
        """删除非默认 Network ACL"""
        ids = []
        for acl in self.vpc.network_acls.all():
            if not acl.is_default:
                ids.append(acl.id)
                acl.delete()
        return ids

    def delete_security_groups(self):
        """删除非默认安全组"""
        ids = []
        for sg in self.vpc.security_groups.all():
            if sg.group_name != 'default':
                ids.append(sg.id)
                sg.delete()
        return ids

    def release_static_ips(self):
        """释放所有 EIP"""
        ids = []
        for addr in self._client.describe_addresses(
            Filters=[{'Name': 'tag:Flag', 'Values': [self.dcName]}]
        ).get('Addresses', []):
            if addr.get('AssociationId'):
                self._client.disassociate_address(AssociationId=addr['AssociationId'])
            self._client.release_address(AllocationId=addr['AllocationId'])
            ids.append(addr['AllocationId'])
        return ids

    def delete_subnets(self):
        """删除所有子网及其网络接口"""
        ids = []
        for subnet in self.vpc.subnets.all():
            ids.append(subnet.id)
            for eni in subnet.network_interfaces.all():
                eni.delete()
            subnet.delete()
        return ids

    def delete_route_tables(self):
        """删除非 main 路由表"""
        ids = []
        for rt in self.vpc.route_tables.all():
            if not any(a.get('Main') for a in rt.associations_attribute):
                ids.append(rt.id)
                rt.delete()
        return ids

    def delete_internet_gateways(self):
        """分离并删除 IGW"""
        ids = []
        for igw in self.vpc.internet_gateways.all():
            self.vpc.detach_internet_gateway(InternetGatewayId=igw.id)
            ids.append(igw.id)
            igw.delete()
        return ids

    def delete_vpc(self):
        """删除 VPC"""
        self.vpc.delete()

    def delete_metadata(self):
        """删除数据库记录"""
        from easyun import db
        dc_record = Datacenter.query.filter_by(name=self.dcName).first()
        if dc_record:
            db.session.delete(dc_record)
            db.session.commit()

    # --- 参数查询 ---

    def list_images(self, arch=None, os_type=None):
        return EC2Server.list_images(self._session, arch, os_type)

    def list_instance_types(self, arch=None, family=None):
        return EC2Server.list_instance_types(self._session, arch, family)

    def list_instance_families(self):
        from .resource.compute.ec2_instype import Instance_Family
        return Instance_Family

    def get_instance_pricing(self, instance_type, os_code=None):
        from .management.sdk_pricing import AwsPricing
        from easyun.common.models import Datacenter as DcModel
        dc = DcModel.query.filter_by(name=self.dcName).first()
        return AwsPricing().ec2_monthly_cost(dc.get_region(), instance_type, os_code)

    def get_cost_summary(self, period='monthly'):
        """获取费用汇总"""
        from .management.sdk_cost import CostExplorer, get_ce_region
        from easyun.common.models import Account
        thisAccount = Account.query.first()
        ceRegion = get_ce_region(thisAccount.aws_type)
        return CostExplorer(self.dcName, region=ceRegion)

    # --- Dashboard 查询 ---

    def get_region_info(self):
        """获取当前 datacenter 所在 region 的信息"""
        from .region import AWS_Regions
        thisDC = Datacenter.query.filter_by(name=self.dcName).first()
        dcRegion = thisDC.get_region()
        regionDict = next((r for r in AWS_Regions if r['regionCode'] == dcRegion), None)
        if regionDict:
            return {
                'icon': regionDict.get('countryCode'),
                'name': regionDict.get('regionName', {}).get('eng'),
            }
        return {'icon': '', 'name': dcRegion}

    def get_az_summary(self):
        """获取各 AZ 的子网数量汇总"""
        azs = self._client.describe_availability_zones()['AvailabilityZones']
        regionInfo = self.get_region_info()
        result = []
        for az in azs:
            azName = az['ZoneName']
            subnets = self._client.describe_subnets(
                Filters=[self.tagFilter, {'Name': 'availability-zone', 'Values': [azName]}]
            ).get('Subnets', [])
            subnetNum = len(subnets)
            result.append({
                'azName': azName,
                'azStatus': 'running' if subnetNum else 'empty',
                'subnetNum': subnetNum,
                'dcRegion': regionInfo,
            })
        return result

    def get_cloudwatch_alarms(self):
        """获取 CloudWatch 告警汇总"""
        cw = self._session.client('cloudwatch')
        alarms = {'iaNum': 0, 'okNum': 0, 'isNum': 0}
        alarm_map = {'OK': 'okNum', 'INSUFFICIENT_DATA': 'isNum', 'ALARM': 'iaNum'}
        res = cw.describe_alarms()
        for alarm_type in ['CompositeAlarms', 'MetricAlarms']:
            for alarm in res.get(alarm_type, []):
                key = alarm_map.get(alarm.get('StateValue'))
                if key:
                    alarms[key] += 1
        return alarms

    def get_cloudwatch_dashboards(self):
        """获取 CloudWatch Dashboard 列表"""
        cw = self._session.client('cloudwatch')
        thisDC = Datacenter.query.filter_by(name=self.dcName).first()
        region = thisDC.get_region()
        prefix = f"https://console.aws.amazon.com/cloudwatch/home?region={region}#dashboards:name="
        res = cw.list_dashboards()
        return [{'title': d['DashboardName'], 'url': prefix + d['DashboardName']} for d in res.get('DashboardEntries', [])]

    def wait_nat_gateway_available(self, natgw_id):
        """等待 NAT Gateway 可用"""
        self._client.get_waiter('nat_gateway_available').wait(NatGatewayIds=[natgw_id])
