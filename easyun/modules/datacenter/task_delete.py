# -*- coding: utf-8 -*-
"""
  @module:  DataCenter Task - Delete
  @desc:    delete datacenter and all associated resources
"""

from easyun.cloud import get_datacenter
from botocore.exceptions import ClientError
from . import logger


def delete_dc_task(self, parm, region):
    """删除 DataCenter 异步任务"""
    try:
        dcName = parm['dcName']
        dc = get_datacenter(dcName)

        def progress(pct, stage):
            logger.info(stage)
            self.update_state(state='PROGRESS', meta={'current': pct, 'total': 100, 'stage': stage})

        # 检查 VPC 是否存在
        try:
            vpcState = dc.vpc.state
        except ClientError:
            vpcState = None
            progress(80, f"[VPC] {dc.vpcId} does not exist")

        if vpcState == 'available':
            self.update_state(state='STARTED', meta={'current': 1, 'total': 100})

            # Step 1: NAT Gateways
            try:
                ids = dc.delete_nat_gateways()
                progress(15, f"[NatGateway] {ids} deleted")
            except Exception as ex:
                return {'message': str(ex), 'status_code': 2110}

            # Step 2: Network ACLs
            try:
                ids = dc.delete_network_acls()
                progress(25, f"[NetworkACL] {ids} deleted")
            except Exception as ex:
                return {'message': str(ex), 'status_code': 2110}

            # Step 3: Security Groups
            try:
                ids = dc.delete_security_groups()
                progress(35, f"[SecurityGroup] {ids} deleted")
            except Exception as ex:
                return {'message': str(ex), 'status_code': 2120}

            # Step 4: Static IPs
            try:
                ids = dc.release_static_ips()
                progress(40, f"[StaticIP] {ids} released")
            except Exception as ex:
                return {'message': str(ex), 'status_code': 2130}

            # Step 5: Subnets
            try:
                ids = dc.delete_subnets()
                progress(50, f"[Subnet] {ids} deleted")
            except Exception as ex:
                return {'message': str(ex), 'status_code': 2150}

            # Step 6: Route Tables
            try:
                ids = dc.delete_route_tables()
                progress(60, f"[RouteTable] {ids} deleted")
            except Exception as ex:
                return {'message': str(ex), 'status_code': 2160}

            # Step 7: Internet Gateways
            try:
                ids = dc.delete_internet_gateways()
                progress(70, f"[InternetGateway] {ids} deleted")
            except Exception as ex:
                return {'message': str(ex), 'status_code': 2170}

            # Step 8: VPC
            try:
                dc.delete_vpc()
                progress(80, f"[VPC] {dc.vpcId} deleted")
            except Exception as ex:
                return {'message': str(ex), 'status_code': 2180}

        # Step 9: DB metadata
        try:
            dc.delete_metadata()
            progress(95, f"[DataCenter] {dcName} metadata deleted")
        except Exception as ex:
            return {'message': str(ex), 'status_code': 2190}

        # Done
        stage = f"[DataCenter] {dcName} deleted successfully !"
        logger.info(stage)
        self.update_state(state='SUCCESS', meta={'current': 100, 'total': 100, 'stage': stage})
        return {
            'detail': {
                'dcName': dcName, 'regionCode': dc.dcName,
                'vpcId': dc.vpcId,
            }
        }
    except Exception as ex:
        return {'message': str(ex), 'status_code': 2199}
