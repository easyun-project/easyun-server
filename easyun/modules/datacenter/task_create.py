# -*- coding: utf-8 -*-
"""
  @module:  DataCenter Task
  @desc:    create datacenter tasks including add new vpc, subnet, securitygroup, etc.
"""
from easyun.cloud import create_datacenter
from easyun.libs.utils import load_json_config
from easyun.common.models import Account
from . import logger


def create_dc_task(self, parm, user):
    """创建 DataCenter 异步任务"""
    dcName = parm['dcName']
    dcRegion = parm['dcRegion']

    logger.info(self.id)
    self.update_state(state='STARTED', meta={'current': 1, 'total': 100})

    def progress(pct, stage):
        logger.info(stage)
        self.update_state(state='PROGRESS', meta={'current': pct, 'total': 100, 'stage': stage})

    # Step 1: 创建 DataCenter 逻辑容器（写 DB）
    try:
        accountId = parm.get('accountId') or Account.query.first().account_id
        dc = create_datacenter(name=dcName, region=dcRegion, account_id=accountId, user=user)
        progress(5, f"[DataCenter] {dcName} created")
    except Exception as ex:
        return {'message': str(ex), 'status_code': 2020}

    # Step 2: 创建 VPC
    try:
        vpc = dc.create_vpc(parm['dcVPC']['cidrBlock'])
        progress(10, f"[VPC] {vpc.id} created")
    except Exception as ex:
        logger.error('[VPC]' + str(ex))
        return {'message': str(ex), 'status_code': 2010}

    # Step 3: create Internet Gateway
    try:
        igw = dc.create_int_gateway(tag_name=parm['pubSubnet1']['gwName'])
        progress(15, f"[InternetGateway] {igw.id} created")
        dc.attach_igw(igw.id)
        progress(20, f"[InternetGateway] {igw.id} attached to {vpc.id}")
    except Exception as ex:
        return {'message': str(ex), 'status_code': 2030}

    # Step 4: create 2x Public Subnets
    try:
        pubsbn1 = dc.create_subnet(parm['pubSubnet1']['cidrBlock'], parm['pubSubnet1']['azName'], parm['pubSubnet1']['tagName'])
        progress(25, f"[Subnet] {pubsbn1.id} created")
        pubsbn2 = dc.create_subnet(parm['pubSubnet2']['cidrBlock'], parm['pubSubnet2']['azName'], parm['pubSubnet2']['tagName'])
        progress(30, f"[Subnet] {pubsbn2.id} created")
    except Exception as ex:
        return {'message': str(ex), 'status_code': 2040}

    # Step 5: update main route table (route to IGW)
    try:
        for rtb in vpc.route_tables.all():
            if rtb.associations_attribute[0]['Main']:
                rtb.create_tags(Tags=[{'Key': 'Flag', 'Value': dcName}, {'Key': 'Name', 'Value': parm['pubSubnet1']['routeTable']}])
                dc.add_route(rtb.id, '0.0.0.0/0', gateway_id=igw.id)
                dc.associate_subnet_to_rtb(rtb.id, pubsbn1.id)
                dc.associate_subnet_to_rtb(rtb.id, pubsbn2.id)
                break
        progress(40, "[RouteTable] public route configured")
    except Exception as ex:
        return {'message': str(ex), 'status_code': 2050}

    # Step 6: create 2x Private Subnets
    try:
        prisbn1 = dc.create_subnet(parm['priSubnet1']['cidrBlock'], parm['priSubnet1']['azName'], parm['priSubnet1']['tagName'])
        progress(45, f"[Subnet] {prisbn1.id} created")
        prisbn2 = dc.create_subnet(parm['priSubnet2']['cidrBlock'], parm['priSubnet2']['azName'], parm['priSubnet2']['tagName'])
        progress(50, f"[Subnet] {prisbn2.id} created")
    except Exception as ex:
        return {'message': str(ex), 'status_code': 2060}

    # Step 7 & 8: NAT Gateway (optional)
    if parm.get('createNatGW'):
        try:
            eip = dc.create_staticip(tag_name=dcName.lower() + "-natgw-eip")
            progress(55, f"[StaticIP] {eip.id} created")
        except Exception as ex:
            return {'message': str(ex), 'status_code': 2071}

        try:
            natgw = dc.create_nat_gateway('public', pubsbn1.id, eip.eipObj['AllocationId'], tag_name=parm['priSubnet1']['gwName'])
            progress(65, f"[NatGateway] {natgw.id} creating")
            # wait for NAT gateway
            dc.wait_nat_gateway_available(natgw.id)
            progress(70, f"[NatGateway] {natgw.id} created")
        except Exception as ex:
            return {'message': str(ex), 'status_code': 2070}

        try:
            nrtb = dc.create_routetable(tag_name=parm['priSubnet1']['routeTable'])
            dc.add_route(nrtb.id, '0.0.0.0/0', nat_gateway_id=natgw.id)
            dc.associate_subnet_to_rtb(nrtb.id, prisbn1.id)
            dc.associate_subnet_to_rtb(nrtb.id, prisbn2.id)
            progress(80, "[RouteTable] private route configured")
        except Exception as ex:
            return {'message': str(ex), 'status_code': 2080}
    else:
        progress(80, "Skip NatGateway")

    # Step 9: Security Groups
    secgroupParms = load_json_config('aws_default_parms', 'easyun/cloud/aws/config').get('secgroup')

    # 9-1: update default SG
    try:
        basePerm = _check_perm(parm['securityGroup0'])
        for sg in vpc.security_groups.all():
            if sg.group_name == 'default':
                sg.create_tags(Tags=[{'Key': 'Flag', 'Value': dcName}, {'Key': 'Name', 'Value': parm['securityGroup0']['tagName']}])
                sg.authorize_ingress(IpPermissions=basePerm)
                break
        progress(85, f"[SecurityGroup] default updated")
    except Exception as ex:
        return {'message': str(ex), 'status_code': 2091}

    # 9-2: create webapp SG
    try:
        sgWeb = dc.create_secgroup(parm['securityGroup1']['tagName'], 'allow http access to web server', parm['securityGroup1']['tagName'])
        webPerm = secgroupParms.get('webPerm', []) + _check_perm(parm['securityGroup1'])
        sgWeb.sgObj.authorize_ingress(IpPermissions=webPerm)
        progress(90, f"[SecurityGroup] {sgWeb.sgObj.group_name} created")
    except Exception as ex:
        return {'message': str(ex), 'status_code': 2092}

    # 9-3: create database SG
    try:
        sgDb = dc.create_secgroup(parm['securityGroup2']['tagName'], 'allow tcp access to database server', parm['securityGroup2']['tagName'])
        dbPerm = secgroupParms.get('dbPerm', []) + _check_perm(parm['securityGroup2'])
        sgDb.sgObj.authorize_ingress(IpPermissions=dbPerm)
        progress(95, f"[SecurityGroup] {sgDb.sgObj.group_name} created")
    except Exception as ex:
        return {'message': str(ex), 'status_code': 2093}

    # Step 10: done
    stage = f"[DataCenter] {dcName} created successfully !"
    logger.info(stage)
    self.update_state(state='SUCCESS', meta={'current': 100, 'total': 100, 'stage': stage})
    return {
        'detail': {
            'dcName': dcName, 'regionCode': dcRegion,
            'vpcId': dc.vpcId, 'createUser': user, 'accountId': accountId,
        }
    }


def _check_perm(sg):
    """根据勾选状态匹配 SecGroup IP 规则"""
    perms = []
    if sg.get('enableRDP'):
        perms.append({'IpProtocol': 'tcp', 'FromPort': 3389, 'ToPort': 3389, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]})
    if sg.get('enableSSH'):
        perms.append({'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]})
    if sg.get('enablePing'):
        perms.append({'IpProtocol': 'icmp', 'FromPort': 8, 'ToPort': -1, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]})
    return perms
