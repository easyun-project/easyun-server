# -*- coding: utf-8 -*-
"""
  @module:  Volume (ebs) SDK Module
  @desc:    AWS SDK Boto3 EC2 Client and Resource Wrapper. 
  @auth:    
"""
import boto3
from easyun.libs.utils import load_json_config
from easyun.modules.mstorage.schemas import VolumeDetail
from .utils import query_dc_region, get_server_name



# 定义系统盘路径
SystemDisk = ['/dev/xvda','/dev/sda1']
# 定义Volume types
VolumeTypes = load_json_config('aws_ebs_types')


class EC2Volume(object):
    def __init__(self, dcName):        
        self._resource = boto3.resource('ec2')
        self._client = self._resource.meta.client
        self.dcName = dcName
        self.tagFilter = { 'Name': 'tag:Flag',  'Values': [dcName] }

    def list_all_volume(self):
        try:
            volumes = self._client.describe_volumes(
                Filters=[ self.tagFilter ]
            )['Volumes']
            volumeList = []
            for vol in volumes:
                nameTag = next((tag['Value'] for tag in vol.get('Tags') if tag["Key"] == 'Name'), None)
                attachList = []
                attachs = vol.get('Attachments')
                if attachs:
                    for a in attachs:
                        # 基于卷挂载路径判断disk类型是 system 还是 user
                        diskType = 'system' if a['Device'] in SystemDisk else 'user'
                        attachList.append({
                            'attachPath' : a['Device'],
                            'svrId' : a['InstanceId'],
                            'tagName' : get_server_name(a['InstanceId']),
                            'attachTime': a['AttachTime'],
                            'diskType': diskType,  
                        })
                isAttachable = True if vol['MultiAttachEnabled'] or vol['State'] == 'available' else False      
                volItem = {
                    'volumeId': vol['VolumeId'],
                    'tagName': nameTag,
                    'volumeAz': vol['AvailabilityZone'],
                    'volumeType': vol['VolumeType'],
                    'volumeSize': vol['Size'],                    
                    'volumeState': vol['State'],
                    'isAttachable' : isAttachable,                 
                    'createTime': vol['CreateTime'],
                    'isEncrypted': vol['Encrypted'],
                    'isMultiAttach' : vol['MultiAttachEnabled'],
        #             'usedSize': none,
                    'volumeIops': vol.get('Iops'),
                    'volumeThruput': vol.get('Throughput'),
                    'volumeAttach': attachList,
                }
                volumeList.append(volItem)
            return volumeList
        except Exception as ex:
            return '%s: %s' %(self.__class__.__name__ ,str(ex))


    def get_volume_list(self):
        try:
            # volumeList = self.list_all_volume()
            # 从volumeList中筛选出基础字段返回
            # listKeys = ['volumeId', 'tagName', 'volumeAz', 'volumeType', 'volumeSize', 'volumeState', 'isAttachable']
            # newVolList = [{k:v for k,v in vol.items() if k in listKeys} for vol in volumeList]
            # return newVolList
            volumes = self._client.describe_volumes(
                Filters=[ self.tagFilter ]
            )['Volumes']
            volumeList = []
            for vol in volumes:
                nameTag = next((tag['Value'] for tag in vol.get('Tags') if tag["Key"] == 'Name'), None)
                isAttachable = True if vol['MultiAttachEnabled'] or vol['State'] == 'available' else False
                volItem = {
                    'volumeId': vol['VolumeId'],
                    'tagName': nameTag,
                    'volumeAz': vol['AvailabilityZone'],
                    'volumeType': vol['VolumeType'],
                    'volumeSize': vol['Size'],        
                    'volumeState': vol['State'],
                    'isAttachable' : isAttachable,                 
                    'createTime': vol['CreateTime'],
                    'isEncrypted': vol['Encrypted'], 
                    'isMultiAttach' : vol['MultiAttachEnabled'],
                    'volumeIops': vol.get('Iops'),
                    'volumeThruput': vol.get('Throughput'),
                }
                volumeList.append(volItem)
            return volumeList
        except Exception as ex:
            return '%s: %s' %(self.__class__.__name__ ,str(ex)) 

    def get_volume_detail(self, volume_id):
        try:
            thisVol = self._resource.Volume(volume_id)
            # 判断flagTag 确保volume在所指的datacenter内
            # if thisVol.tags:
            #     flagTag = next((tag['Value'] for tag in thisVol.tags if tag['Key'] == 'Flag'), None)
            #     if flagTag != dcName:
            #         raise ValueError(f"The volume {vol_id} does not exist in datacenter {dcName}.")
            #     nameTag = next((tag['Value'] for tag in thisVol.tags if tag['Key'] == 'Name'), None)                
            # else:
            #     raise ValueError(f"The volume {vol_id} does not exist in datacenter {dcName}.")            
            nameTag = next((tag['Value'] for tag in thisVol.tags if tag['Key'] == 'Name'), None)
            isAttachable = True if thisVol.multi_attach_enabled or thisVol.state == 'available' else False
            attachList = []
            attachs = thisVol.attachments
            if attachs:
                for a in attachs:
                    # 基于卷挂载路径判断disk类型是 system 还是 user
                    diskType = 'system' if a['Device'] in SystemDisk else 'user'
                    attachList.append({
                        'attachPath' : a['Device'],
                        'svrId' : a['InstanceId'],
                        'tagName' : get_server_name(a['InstanceId']),
                        'attachTime': a['AttachTime'],
                        'diskType': diskType,
                    })
            volumeBasic = {
                'volumeId': thisVol.volume_id,
                'tagName' : nameTag,
                'isAttachable' : isAttachable,
                'volumeState': thisVol.state,                
                'volumeAz': thisVol.availability_zone,
                'volumeType': thisVol.volume_type,
                'createTime': thisVol.create_time,
            }
            volumeConfig = {
                'volumeSize': thisVol.size,
                'volumeIops': thisVol.iops,
                'volumeThruput': thisVol.throughput,
                'isEncrypted': thisVol.encrypted,
            }
            # userTags = [{k:v for k,v in tag.items() if k not in ["Flag","Name"]} for tag in thisVol.tags]
            userTags = [t for t in thisVol.tags if t['Key'] not in ['Flag',]]
            
            VolumeDetail = {
                'volumeBasic':volumeBasic,                
                'volumeConfig':volumeConfig,
                'volumeAttach':attachList,
                'userTags':userTags
            }
            return VolumeDetail
        except Exception as ex:
            return '%s: %s' %(self.__class__.__name__ ,str(ex))

    def create_volume(self):
        try:

            return 
        except Exception as ex:
            return '%s: %s' %(self.__class__.__name__ ,str(ex))

    def delete_volume(self):
        try:

            return 
        except Exception as ex:
            return '%s: %s' %(self.__class__.__name__ ,str(ex))

    def attach_to_server(self):
        try:

            return 
        except Exception as ex:
            return '%s: %s' %(self.__class__.__name__ ,str(ex))

    def detach_from_server(self):
        try:

            return 
        except Exception as ex:
            return '%s: %s' %(self.__class__.__name__ ,str(ex))
