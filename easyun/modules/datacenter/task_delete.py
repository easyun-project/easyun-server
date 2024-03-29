# -*- coding: utf-8 -*-
"""
  @module:  DataCenter Task
  @desc:    create datacenter tasks including add new vpc, subnet, securitygroup, etc.
  @auth:    aleck
"""

import boto3
from botocore.exceptions import ClientError
from easyun import db, celery
from easyun.common.models import Datacenter
from . import logger


@celery.task(bind=True)
def delete_dc_task(self, parm, region):
    """
    删除 DataCenter 异步任务
    按步骤进行，步骤失败直接返回
    :return {message,status_code,http_code:200}
    """
    try:
        # Datacenter basic attribute define
        dcName = parm['dcName']
        resource_ec2 = boto3.resource('ec2', region_name=region)
        thisDC: Datacenter = Datacenter.query.filter_by(name=dcName).first()
        thisVPC = resource_ec2.Vpc(thisDC.vpc_id)
        try:
            # 'State': 'pending'|'available'
            vpcState = thisVPC.state
        except ClientError:
            vpcState = None
            stage = f"[VPC] {thisDC.vpc_id}  does not exist."
            logger.info(stage)
            self.update_state(
                state='PROGRESS', meta={'current': 80, 'total': 100, 'stage': stage}
            )

        if vpcState == 'available':
            # Step 0:  Check the prerequisites for deleting a datacenter
            # when prerequisites check Ok
            logger.info(self.request.id)
            self.update_state(state='STARTED', meta={'current': 1, 'total': 100})

            # Step 1: delete NAT Gateway in the VPC
            try:
                natgwList = []
                natgws = resource_ec2.meta.client.describe_nat_gateways(
                    Filters=[
                        {'Name': 'tag:Flag', 'Values': [dcName]},
                    ]
                )['NatGateways']
                for natgw in natgws:
                    if natgw.get('State') != 'deleted':
                        delNatGw = resource_ec2.meta.client.delete_nat_gateway(
                            NatGatewayId=natgw['NatGatewayId']
                        )['NatGatewayId']

                    stage = f"[NatGateway] {natgw['NatGatewayId']} deleting ..."
                    logger.info(stage)
                    self.update_state(
                        state='PROGRESS', meta={'current': 5, 'total': 100, 'stage': stage}
                    )

                    # waite natgw deleted
                    waiter = resource_ec2.meta.client.get_waiter('nat_gateway_deleted')
                    waiter.wait(NatGatewayIds=[natgw['NatGatewayId']])

                    natgwList.append(delNatGw)

                stage = f"[NatGateway] {natgwList} deleted"
                logger.info(stage)
                self.update_state(
                    state='PROGRESS', meta={'current': 15, 'total': 100, 'stage': stage}
                )

            except Exception as ex:
                return {
                    'message': str(ex),
                    'status_code': 2110,
                    # 'http_status_code': 400,
                }

            # You must detach or delete all gateways and resources that are associated with the VPC before you can delete it.
            # Step 2: delete all network_acls associated with the VPC (except the default one)
            try:
                aclList = []
                for netacl in thisVPC.network_acls.all():
                    if not netacl.is_default:
                        aclList.append(netacl.id)
                        netacl.delete()

                stage = f"[NetworkACL] {aclList} deleted"
                logger.info(stage)
                self.update_state(
                    state='PROGRESS', meta={'current': 25, 'total': 100, 'stage': stage}
                )

            except Exception as ex:
                return {
                    'message': str(ex),
                    'status_code': 2110,
                }

            # Step 3: delete all security groups associated with the VPC (except the default one)
            try:
                sgList = []
                for sg in thisVPC.security_groups.all():
                    if sg.group_name != 'default':
                        sgList.append(sg.id)
                        sg.delete()

                stage = f"[SecurityGroup] {sgList} deleted"
                logger.info(stage)
                self.update_state(
                    state='PROGRESS', meta={'current': 35, 'total': 100, 'stage': stage}
                )

            except Exception as ex:
                return {
                    'message': str(ex),
                    'status_code': 2120,
                }

            # Step 4: delete all eip associated with the datacenter
            try:
                eipList = []

                stage = f"[StaticIP] {eipList} deleted"
                logger.info(stage)
                self.update_state(
                    state='PROGRESS', meta={'current': 40, 'total': 100, 'stage': stage}
                )

            except Exception as ex:
                return {
                    'message': str(ex),
                    'status_code': 2130,
                }

            # Step 5: delete requested_vpc_peering_connections associated with the VPC

            # Step 5: delete all subnets and network_interfaces associated with the VPC
            try:
                subnetList = []
                for subnet in thisVPC.subnets.all():
                    subnetList.append(subnet.id)
                    for interface in subnet.network_interfaces.all():
                        interface.delete()
                    subnet.delete()

                stage = f"[Subnet] {subnetList} deleted"
                logger.info(stage)
                self.update_state(
                    state='PROGRESS', meta={'current': 50, 'total': 100, 'stage': stage}
                )

            except Exception as ex:
                return {
                    'message': str(ex),
                    'status_code': 2150,
                }

            # Step 6: delete all route tables associated with the VPC (except the default one)
            try:
                rtbList = []
                for rtb in thisVPC.route_tables.all():
                    assList = [a['Main'] for a in rtb.associations_attribute]
                    if True not in assList:
                        # 自动创建的main route table随vpc一起删
                        rtbList.append(rtb.id)
                        rtb.delete()

                stage = f"[RouteTable] {rtbList} deleted"
                logger.info(stage)
                self.update_state(
                    state='PROGRESS', meta={'current': 60, 'total': 100, 'stage': stage}
                )

            except Exception as ex:
                return {
                    'message': str(ex),
                    'status_code': 2160,
                }

            # Step 7: delete internet_gateways associated with the VPC
            try:
                igwList = []
                for igw in thisVPC.internet_gateways.all():
                    thisVPC.detach_internet_gateway(InternetGatewayId=igw.id)
                    igwList.append(igw.id)
                    igw.delete()

                stage = f"[InternetGateway] {igwList} deleted"
                logger.info(stage)
                self.update_state(
                    state='PROGRESS', meta={'current': 70, 'total': 100, 'stage': stage}
                )

            except Exception as ex:
                return {
                    'message': str(ex),
                    'status_code': 2170,
                }

            # Step 8: delete  easyun vpc, including:
            try:
                thisVPC.delete()
                stage = f"[VPC] {thisVPC.id} deleted"
                logger.info(stage)
                self.update_state(
                    state='PROGRESS', meta={'current': 80, 'total': 100, 'stage': stage}
                )

            except Exception as ex:
                return {
                    'message': str(ex),
                    'status_code': 2180,
                }

        # step 9: Update local Datacenter metadata
        try:
            # curr_user = user
            db.session.delete(thisDC)
            db.session.commit()

            stage = f"[DataCenter]' {thisDC.name} metadata updated."
            logger.info(stage)
            self.update_state(
                state='PROGRESS', meta={'current': 95, 'total': 100, 'stage': stage}
            )

        except Exception as ex:
            return {'message': str(ex), 'status_code': 2190, 'http_status_code': 400}

        # step 10: Delete Datacenter name list from DynamoDB
        try:
            # 待实现
            stage = f"[DataCenter]' {thisDC.name} deleted successfully !"
            logger.info(stage)
            self.update_state(
                state='SUCCESS', meta={'current': 100, 'total': 100, 'stage': stage}
            )

        except Exception as ex:
            return {'message': str(ex), 'status_code': 2191, 'http_status_code': 400}

        return {
            'detail': {
                'dcName': thisDC.name,
                'regionCode': thisDC.region,
                'vpcId': thisDC.vpc_id,
                'accountId': thisDC.account_id,
            }
        }
    except Exception as ex:
        return {'message': str(ex), 'status_code': 2199, 'http_status_code': 400}
