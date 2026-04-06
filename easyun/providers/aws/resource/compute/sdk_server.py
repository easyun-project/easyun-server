# -*- coding: utf-8 -*-
"""
  @module:  Server (ec2) SDK Module
  @desc:    AWS SDK Boto3 EC2 Client and Resource Wrapper.
"""

from botocore.exceptions import ClientError
from ...session import get_easyun_session
from easyun.providers.base import ComputeInstanceBase


class EC2Server(ComputeInstanceBase):
    def __init__(self, svr_id, dc_name=None):
        self.id = svr_id
        session = get_easyun_session(dc_name)
        self._ec2_client = session.client('ec2')
        self._ec2_resource = session.resource('ec2')
        try:
            self.svrObj = self._ec2_resource.Instance(self.id)
            self.tagName = next(
                (tag['Value'] for tag in (self.svrObj.tags or []) if tag['Key'] == 'Name'), None
            )
        except ClientError as ex:
            raise ex

    def get_detail(self):
        """获取服务器详情（详情页用）"""
        try:
            s = self.svrObj
            client = self._ec2_client
            resource = self._ec2_resource

            inst = client.describe_instances(InstanceIds=[self.id])
            inst_res = [j for i in inst['Reservations'] for j in i['Instances']][0]

            insInfo = client.describe_instance_types(InstanceTypes=[s.instance_type])
            vCpu = insInfo['InstanceTypes'][0]['VCpuInfo']['DefaultVCpus']
            memory = insInfo['InstanceTypes'][0]['MemoryInfo']['SizeInMiB'] / 1024

            images = client.describe_images(ImageIds=[s.image_id])
            if images['Images']:
                img = images['Images'][0]
                arch = img['Architecture']
                imageName = img['Name'].split('/')[-1]
                imagePath = '/'.join(img['ImageLocation'].split('/')[1:])
            else:
                arch, imageName, imagePath = 'unknown', 'unknown', 'unknown'

            protection = client.describe_instance_attribute(
                InstanceId=self.id, Attribute='disableApiTermination'
            )['DisableApiTermination']['Value']

            association = inst_res.get('NetworkInterfaces', [{}])[0].get('Association') if inst_res.get('NetworkInterfaces') else None

            svrProperty = {
                'instanceName': self.tagName,
                'instanceType': s.instance_type,
                'vCpu': vCpu,
                'memory': memory,
                'privateIp': inst_res.get('PrivateIpAddress'),
                'publicIp': s.public_ip_address,
                'isEip': bool(association and association.get('IpOwnerId') != 'amazon'),
                'status': s.state['Name'],
                'instanceId': self.id,
                'launchTime': inst_res['LaunchTime'].isoformat(),
                'privateIpv4Dns': inst_res.get('PrivateDnsName'),
                'publicIpv4Dns': inst_res.get('PublicDnsName'),
                'platformDetails': inst_res.get('PlatformDetails'),
                'virtualization': inst_res.get('VirtualizationType'),
                'tenancy': 'default',
                'usageOperation': inst_res.get('UsageOperation'),
                'monitoring': inst_res['Monitoring']['State'],
                'terminationProtection': 'disabled' if protection else 'enabled',
                'amiId': s.image_id,
                'amiName': imageName,
                'amiPath': imagePath,
                'keyPairName': inst_res.get('KeyName'),
                'iamRole': inst_res.get('IamInstanceProfile', {}).get('Arn', '').split('/')[-1] if inst_res.get('IamInstanceProfile') else '',
            }
            svrConfig = {'arch': arch, 'os': 'amzn2'}
            svrDisk = {'volumeIds': [v['Ebs']['VolumeId'] for v in inst_res.get('BlockDeviceMappings', [])]}
            svrNetworking = {'privateIp': inst_res.get('PrivateIpAddress'), 'publicIp': s.public_ip_address}
            svrSecurity = [{'sgId': g['GroupId'], 'sgName': g['GroupName']} for g in inst_res.get('SecurityGroups', [])]
            svrTags = [t for t in (inst_res.get('Tags') or []) if t['Key'] not in ['Flag', 'Name']]
            svrConnect = {'userName': 'ec2-user', 'publicIp': s.public_ip_address}

            return {
                'svrProperty': svrProperty,
                'svrConfig': svrConfig,
                'svrDisk': svrDisk,
                'svrNetworking': svrNetworking,
                'svrSecurity': svrSecurity,
                'svrTags': svrTags,
                'svrConnect': svrConnect,
            }
        except Exception as ex:
            raise ex

    def get_instype_param(self):
        """获取实例类型参数"""
        s = self.svrObj
        return {
            'insArch': s.architecture,
            'insHyper': s.hypervisor,
            'insType': s.instance_type,
            'imgID': s.image_id,
        }

    def get_tags(self):
        try:
            return [t for t in (self.svrObj.tags or []) if t['Key'] not in ['Flag']]
        except Exception:
            return []

    def add_tag(self, tag):
        """新增/修改 tag"""
        if tag.get('Key') == 'Flag':
            raise ValueError('Flag tag unsupported')
        self.svrObj.create_tags(Tags=[tag])
        return self.get_tags()

    def remove_tag(self, tag):
        """删除 tag"""
        if tag.get('Key') == 'Flag':
            raise ValueError('Flag tag unsupported')
        self.svrObj.delete_tags(Tags=[tag])
        return self.get_tags()

    def attach_disk(self, volume_id, device_path):
        volume = self._ec2_resource.Volume(volume_id)
        volume.attach_to_instance(Device=device_path, InstanceId=self.id)

    def detach_disk(self, volume_id, device_path):
        volume = self._ec2_resource.Volume(volume_id)
        volume.detach_from_instance(Device=device_path, InstanceId=self.id)

    def attach_eip(self, public_ip):
        self._ec2_client.associate_address(InstanceId=self.id, PublicIp=public_ip)

    def detach_eip(self, public_ip):
        resp = self._ec2_client.describe_addresses(PublicIps=[public_ip])
        assoc_id = resp['Addresses'][0]['AssociationId']
        self._ec2_client.disassociate_address(AssociationId=assoc_id)

    def attach_secgroup(self, sg_id):
        for eni in self.svrObj.network_interfaces:
            group_ids = [g['GroupId'] for g in eni.groups]
            group_ids.append(sg_id)
            eni.modify_attribute(Groups=group_ids)

    def detach_secgroup(self, sg_id):
        for eni in self.svrObj.network_interfaces:
            group_ids = [g['GroupId'] for g in eni.groups if g['GroupId'] != sg_id]
            if not group_ids:
                raise ValueError('You must specify at least one group')
            eni.modify_attribute(Groups=group_ids)

    def set_name(self, name):
        self.svrObj.create_tags(Tags=[{'Key': 'Name', 'Value': name}])
        self.tagName = name

    def set_protection(self, disable):
        self.svrObj.modify_attribute(DisableApiTermination={'Value': disable})

    def set_instance_type(self, instance_type):
        if self.svrObj.state['Name'] != 'stopped':
            raise ValueError('Server must be stopped.')
        self.svrObj.modify_attribute(InstanceType={'Value': instance_type})

    def start(self):
        self.svrObj.start()
        return {'instanceId': self.id, 'action': 'start'}

    def stop(self):
        self.svrObj.stop()
        return {'instanceId': self.id, 'action': 'stop'}

    def reboot(self):
        self.svrObj.reboot()
        return {'instanceId': self.id, 'action': 'reboot'}

    def delete(self):
        self.svrObj.terminate()
        return {'instanceId': self.id, 'action': 'terminate'}

    @classmethod
    def list_images(cls, session, arch=None, os_type=None):
        """列出可用 AMI 列表"""
        from .ec2_ami import AMI_Windows, AMI_Linux
        amiList = AMI_Windows.get(arch, []) if os_type == 'windows' else AMI_Linux.get(arch, [])
        if not amiList:
            return []
        client = session.client('ec2')
        filters = [
            {'Name': 'state', 'Values': ['available']},
            {'Name': 'image-type', 'Values': ['machine']},
            {'Name': 'virtualization-type', 'Values': ['hvm']},
            {'Name': 'architecture', 'Values': [arch]},
            {'Name': 'name', 'Values': [a['amiName'] for a in amiList]},
        ]
        images = client.describe_images(Filters=filters)['Images']
        return [
            {
                'imgID': img['ImageId'],
                'osName': next((a['osName'] for a in amiList if a['amiName'] == img['Name']), ''),
                'osVersion': next((a['osVersion'] for a in amiList if a['amiName'] == img['Name']), ''),
                'osCode': next((a['osCode'] for a in amiList if a['amiName'] == img['Name']), ''),
                'imgDescription': img.get('Description', ''),
                'rootDevice': {
                    'devicePath': img['RootDeviceName'],
                    'deviceType': img['RootDeviceType'],
                    'deviceDisk': img['BlockDeviceMappings'][0].get('Ebs') if img.get('BlockDeviceMappings') else None,
                },
            }
            for img in images
        ]

    @classmethod
    def list_instance_types(cls, session, arch=None, family=None):
        """列出可用实例规格"""
        from .ec2_instype import get_family_descode
        client = session.client('ec2')
        filters = [
            {'Name': 'processor-info.supported-architecture', 'Values': [arch]},
            {'Name': 'current-generation', 'Values': ['true']},
        ]
        if family and family != 'all':
            filters.append({'Name': 'instance-type', 'Values': [f'{family}.*']})
        desc_args = {'Filters': filters}
        result_list = []
        while True:
            result = client.describe_instance_types(**desc_args)
            for i in result['InstanceTypes']:
                ins_type = i['InstanceType']
                ins_family = ins_type.split('.')[0]
                result_list.append({
                    'insType': ins_type,
                    'familyName': ins_family,
                    'familyDes': get_family_descode(ins_family),
                    'vcpuNum': i['VCpuInfo']['DefaultVCpus'],
                    'memSize': i['MemoryInfo']['SizeInMiB'] / 1024,
                    'netSpeed': i['NetworkInfo']['NetworkPerformance'],
                })
            if 'NextToken' not in result:
                break
            desc_args['NextToken'] = result['NextToken']
        return result_list
