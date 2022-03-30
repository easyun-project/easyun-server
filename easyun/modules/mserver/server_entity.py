# -*- coding: utf-8 -*-
"""
  @module:  Server Detail
  @desc:    Get Server detail info
  @auth:    
"""

import boto3
from apiflask import Schema, input, output, auth_required
from apiflask.fields import Integer, String, List, Dict
from apiflask.validators import Length, OneOf
from easyun.common.auth import auth_token
from easyun.common.result import Result
from easyun.cloud.aws_ec2_ami import AMI_Windows, AMI_Linux
from .schemas import TagItem
from . import bp



class DetailOut(Schema):
    # ins_id = String()
    # tag_name = Dict()
    # ins_status = String()
    # ins_type = String()
    # vcpu = Integer()
    # ram = String()
    # subnet_id = String()
    # ssubnet_id = String()
    # key_name = String()
    # category = String()
    #缺少ipname，publicip,Terminal protection, IAM role
    InstanceType = String()
    VCpu = String()
    Memory = String()
    PrivateIpAddress = String()
    PublicIpAddress = String()

    InstanceId = String()
    LaunchTime = String()

    PrivateDnsName = String()
    PublicDnsName = String()

    PlatformDetails = String()
    VirtualizationType = String()
    UsageOperation = String()    
    Monitoring = String()

    ImageId = String()
    ImageName = String()
    ImagePath = String()
    KeyName = String()
    IamInstanceProfile = String()
    ServerState = String()
    Tenancy = String()
    TerminalProtection = String()
    BlockDeviceMappings = List(Dict())
    NetworkInterfaces = List(Dict())
    SecurityGroups = List(Dict())
    


@bp.get('/detail/<svr_id>')
@auth_required(auth_token)
# @output(DetailOut, description='Server detail info')
def get_server_detail(svr_id):
    '''获取指定云服务器详情信息'''
    CLIENT = boto3.client('ec2')
    try:
        instance = CLIENT.describe_instances(InstanceIds=[svr_id])

        instance_res = [j for i in instance['Reservations'] for j in i['Instances']][0]
        ec2 = boto3.resource('ec2')
        instance_res1 = ec2.Instance(instance_res['InstanceId'])

        instance_type = CLIENT.describe_instance_types(InstanceTypes=[instance_res['InstanceType']])
        VCpu = instance_type['InstanceTypes'][0]["VCpuInfo"]["DefaultVCpus"]
        Memory = instance_type['InstanceTypes'][0]["MemoryInfo"]["SizeInMiB"]/1024

        images = CLIENT.describe_images(ImageIds=[instance_res['ImageId']])
        if  len(images['Images'])==0:
            tip = "EC2 can't retrieve the {} because the AMI was either deleted or made private"
            arch = tip.format('arch')
            instance_res['ImageName'] = tip.format('ImageName')
            instance_res['ImageFullName'] = tip.format('ImageFullName')
            amitmp = []
            instance_res['ImagePath'] = tip.format('ImagePath')
        else:
            arch = images['Images'][0]['Architecture']
            instance_res['ImageName'] = images["Images"][0]["Name"].split('/')[-1]
            instance_res['ImageFullName'] = images["Images"][0]["Name"]
            print(instance_res['ImageFullName'])
            AMI = AMI_Windows[arch] + AMI_Linux[arch]
            amitmp = [ami for ami in AMI if ami['amiName'] == instance_res['ImageFullName']]
            # print(amitmp)
            # instance_res['ImagePath'] = images["Images"][0]["ImageLocation"]
            instance_res['ImagePath'] = '/'.join(images["Images"][0]["ImageLocation"].split('/')[1:])
        protection = CLIENT.describe_instance_attribute(InstanceId = instance_res['InstanceId'],Attribute = 'disableApiTermination')['DisableApiTermination']['Value']
        # print(images["Images"][0]["ImageLocation"])
        # print(images["Images"][0]["Name"])
        # print(instance_type)
        # print(instance_res)
        
        instance_res['Monitoring'] = instance_res['Monitoring']['State']
        instance_res['VCpu'] = VCpu
        instance_res['Memory'] = Memory
        instance_res['IamInstanceProfile'] = instance_res['IamInstanceProfile']['Arn'].split('/')[-1]

        instance_res['ServerState'] = instance_res['State']['Name']
        instance_res['PublicIpAddress'] = instance_res1.public_ip_address
        instance_res['Tenancy'] = 'default'
        instance_res['TerminalProtection'] = 'disabled' if protection else 'enabled'
        association = instance_res["NetworkInterfaces"][0].get("Association")
        svrProperty = {
            "instanceName":[t for t in instance_res["Tags"] if t['Key'] == "Name"][0]['Value'],
            "instanceType":instance_res["InstanceType"],
            "vCpu":instance_res["VCpu"],
            "memory":instance_res["Memory"],
            "privateIp":instance_res["PrivateIpAddress"],
            "publicIp":instance_res["PublicIpAddress"],
            "isEip": True if association and association["IpOwnerId"]!='amazon' else False ,
            "status":instance_res["ServerState"],

            # "":instance_res[""],
            "instanceId":instance_res['InstanceId'],
            "launchTime":instance_res["LaunchTime"].isoformat(),
            "privateIpv4Dns":instance_res["PrivateDnsName"],
            "publicIpv4Dns":instance_res["PublicDnsName"],


            "platformDetails":instance_res["PlatformDetails"],
            "virtualization":instance_res["VirtualizationType"],
            "tenancy":instance_res["Tenancy"],
            "usageOperation":instance_res["UsageOperation"],
            "monitoring":instance_res["Monitoring"],
            "terminationProtection":instance_res["TerminalProtection"],
            
            "amiId":instance_res["ImageId"],
            "amiName":instance_res["ImageName"],
            "amiPath":instance_res["ImagePath"],
            "keyPairName":instance_res["KeyName"],
            "iamRole":instance_res["IamInstanceProfile"],
        }
        svrConfig = {
            "arch":arch,
            "os":amitmp[0]['osCode'] if amitmp else 'amzn2'
        }
        svrDisk = {
            "volumeIds": [v["Ebs"]['VolumeId'] for v in instance_res["BlockDeviceMappings"]]
        }
        svrNetworking = {
            "privateIp":instance_res["PrivateIpAddress"],
            "publicIp":instance_res["PublicIpAddress"],
        } 
        svrSecurity = [{"sgId":g['GroupId'],"sgName":g['GroupName']} for g in instance_res["SecurityGroups"]]        # {
        #     "sgId":[g['GroupId'] for g in instance_res["SecurityGroups"]],
        #     "sgName":[g['GroupName'] for g in instance_res["SecurityGroups"]],
        # }
        svrTags = [t for t in instance_res["Tags"] if t['Key'] not in ["Flag","Name"]]
        # {
        #     # "":instance_res[""],
        #     "tags":instance_res["Tags"],
        #     # "":instance_res[""],
        # }
        svrConnect = {
            "userName":amitmp[0]['userName'] if amitmp else ['ec2-user'],
            "publicIp":instance_res["PublicIpAddress"],
        }
        detail = {
            "svrProperty":svrProperty,
            "svrConfig":svrConfig,
            "svrDisk":svrDisk,
            "svrNetworking":svrNetworking,
            "svrSecurity":svrSecurity,
            "svrTags":svrTags,
            "svrConnect":svrConnect,
        }
        res = Result(detail , status_code=200)
        return res.make_resp()
    except Exception as e:
        response = Result(
            message=str(e), status_code=3001, http_status_code=400
        )
        response.err_resp()


@bp.get('/instype/<svr_id>')
@auth_required(auth_token)
def get_ins_types(svr_id):
    '''获取指定云服务器实例参数 [测试]'''
    # 用于查询受支持的Instance Family列表)
    try:
        resource_ec2 = boto3.resource('ec2')
        thisSvr = resource_ec2.Instance(svr_id)
        instypeParam = {
            'insArch': thisSvr.architecture,
            'insHyper': thisSvr.hypervisor,
            'insType': thisSvr.instance_type,
            'imgID': thisSvr.image_id
        }

        resp = Result(
            detail = instypeParam, 
            status_code=200
            )
        return resp.make_resp()

    except Exception as ex:
        response = Result(
            message=str(ex), 
            status_code=3001, 
            http_status_code=400
        )
        response.err_resp()

class DiskInfoIn(Schema):
    action = String(required=True, example='attach')
    svrId = String(required=True, example='i-0d05b7bda069b8c1d')  #云服务器ID
    diskPath = String(required=True, example='/dev/sdf')
    volumeId = String(required=True, example='vol-0fcb3e28f8687f74d')  #volumn ID
@bp.put('/disk')
@auth_required(auth_token)
@input(DiskInfoIn)
def attach_disk(param):
    '''云服务器关联与解绑磁盘(volume)'''  
    try:
        # CLIENT = boto3.client('ec2')
        RESOURCE = boto3.resource('ec2')
        volume = RESOURCE.Volume(param['volumeId'])
        # waiter = CLIENT.get_waiter('volume_available')
        # waiter.wait(
        #     VolumeIds=[
        #         volume.id,
        #     ]
        # )
        if param["action"] == "attach":
            volume.attach_to_instance(
                Device=param["diskPath"],
                InstanceId=param["svrId"]
            )
        elif param["action"] == "detach":
            # disks = CLIENT.describe_instances(InstanceIds=[param['svrId']])['Reservations'][0]['Instances'][0]['BlockDeviceMappings']
            # vid = [i['Ebs']['VolumeId'] for i in disks if i['DeviceName'] == param['diskPath']]
            # # print(dir(volume))
            # if len(vid)==0:
            #     raise ValueError('invalid device')
            # volume = RESOURCE.Volume(vid[0])

            volume.detach_from_instance(
                Device=param['diskPath'],
                InstanceId=param['svrId']
            )
        else:
            raise ValueError('invalid action') 
        response = Result(
            detail={'msg':'{} disk success'.format(param["action"])},
            status_code=200
            )
        return response.make_resp()
    except Exception as e:
        response = Result(
            message=str(e), status_code=3001, http_status_code=400
        )
        response.err_resp()

# class DiskDetachInfoIn(Schema):
#     svrId = String(required=True, example='i-03b15ba2fbe4f3a14')  #云服务器ID
#     diskPath = String(required=True, example='/dev/sdg')

# @bp.put('/detach/disk')
# @auth_required(auth_token)
# @input(DiskDetachInfoIn)
# # @output()
# def detach_disk(param):
#     '''云服务器分离磁盘(volume)'''
#     try:
#         CLIENT = boto3.client('ec2')
#         RESOURCE = boto3.resource('ec2')
#         # server =RESOURCE.Instance(param['svrId'])
#         disks = CLIENT.describe_instances(InstanceIds=[param['svrId']])['Reservations'][0]['Instances'][0]['BlockDeviceMappings']
#         vid = [i['Ebs']['VolumeId'] for i in disks if i['DeviceName'] == param['diskPath']]
#         print(vid)
#         # print(dir(volume))
#         if len(vid)==0:
#             raise ValueError('invalid device')
#         volume = RESOURCE.Volume(vid[0])

#         volume.detach_from_instance(
#             Device=param['diskPath'],
#             InstanceId=param['svrId']
#         )
#         # waiter = CLIENT.get_waiter('volume_available')
#         # waiter.wait(
#         #     VolumeIds=[
#         #         volume.id,
#         #     ]
#         # )
#         from time import sleep 
#         while True:
#             volume1 = RESOURCE.Volume(volume.volume_id)
#             print(volume1.state)
#             if volume1.state == 'available':
#                 # volume1.delete()
#                 break
#             sleep(0.5)
        
#         response = Result(
#             detail={'msg':'detach {} success'.format(param['diskPath'])},
#             status_code=200
#             )   

#         return response.make_resp()
#     except Exception as e:
#         response = Result(
#             message=str(e), status_code=3001, http_status_code=400
#         )
#         response.err_resp()


class EipAttachInfoIn(Schema):
    action = String(required=True, example='attach')
    svrId = String(required=True, example='i-0d05b7bda069b8c1d')  #云服务器ID
    publicIp = String(required=True, example='34.192.222.116')


@bp.put('/eip')
@auth_required(auth_token)
@input(EipAttachInfoIn)
def attach_eip(param):
    '''云服务器关联和解绑静态IP(eip)'''
    try:
        CLIENT = boto3.client('ec2')
        if param["action"] == "attach":
            CLIENT.associate_address(
            InstanceId=param['svrId'],
            PublicIp=param['publicIp'],
            )
        elif param["action"] == "detach":
            publicIp = CLIENT.describe_addresses(
            PublicIps = [param['publicIp']],
            )
            associationId = publicIp['Addresses'][0]['AssociationId']
            CLIENT.disassociate_address(
                AssociationId=associationId,
                )
        else:
            raise ValueError('invalid action') 
        response = Result(
            detail={'msg':'{} eip success'.format(param["action"])},
            status_code=200
            )   

        return response.make_resp()
    except Exception as e:
        response = Result(
            message=str(e), status_code=3001, http_status_code=400
        )
        response.err_resp()

# class EipDetachInfoIn(Schema):
#     publicIp = String(required=True, example='52.70.138.156')

# @bp.put('/detach/eip')
# @auth_required(auth_token)
# @input(EipDetachInfoIn)
# def detach_eip(param):
#     '''云服务器分离静态IP(eip)'''
#     try:
#         CLIENT = boto3.client('ec2')
#         publicIp = CLIENT.describe_addresses(
#             PublicIps = [param['publicIp']],
#         )
#         associationId = publicIp['Addresses'][0]['AssociationId']
#         CLIENT.disassociate_address(
#             AssociationId=associationId,
#             )
#         response = Result(
#             detail={'msg':'detach eip success'},
#             status_code=200
#             )   

#         return response.make_resp()
#     except Exception as e:
#         response = Result(
#             message=str(e), status_code=3001, http_status_code=400
#         )
#         response.err_resp()

class SgAttachInfoIn(Schema):
    action = String(required=True, example='attach')
    svrId = String(required=True, example='i-0d05b7bda069b8c1d')  #云服务器ID
    secgroupId = String(required=True, example='sg-0bb69bb599b303a1e')


@bp.put('/secgroup')
@auth_required(auth_token)
@input(SgAttachInfoIn)
def attach_secgroup(param):
    '''云服务器关联和解绑安全组(secgroup)'''
    try:
        ec2 = boto3.resource('ec2')
        if param["action"] == "attach":
            for network_interface in ec2.Instance(param['svrId']).network_interfaces:
                group_ids = [group['GroupId'] for group in network_interface.groups]
                group_ids.append(param['secgroupId'])
                network_interface.modify_attribute(Groups=group_ids)
        elif param["action"] == "detach":
            for network_interface in ec2.Instance(param['svrId']).network_interfaces:
                # group_ids = [group['GroupId'] for group in network_interface.groups]
                group_ids = [group['GroupId'] for group in network_interface.groups if group['GroupId'] !=param['secgroupId']]
                # print(group_ids)
                if len(group_ids)>0:
                    network_interface.modify_attribute(Groups=group_ids)
                else:
                    raise ValueError('You must specify at least one group')
        else:
            raise ValueError('invalid action')  
        
        response = Result(
            detail={'msg':'{} secgroup success'.format(param["action"])},
            status_code=200
            )   

        return response.make_resp()
    except Exception as e:
        response = Result(
            message=str(e), status_code=3001, http_status_code=400
        )
        response.err_resp()

# @bp.put('/detach/secgroup')
# @auth_required(auth_token)
# @input(SgAttachInfoIn)
# def detach_secgroup(param):
#     '''云服务器解绑安全组(secgroup)'''
#     try:
#         ec2 = boto3.resource('ec2')
#         for network_interface in ec2.Instance(param['svrId']).network_interfaces:
#             group_ids = [group['GroupId'] for group in network_interface.groups]
#             if param['secgroupId'] in group_ids:
#                 network_interface.modify_attribute(Groups=[group_id for group_id in group_ids if group_id !=param['secgroupId']])
#         response = Result(
#             detail={'msg':'detach secgroup success'},
#             status_code=200
#             ) 
#         return response.make_resp() 
#     except Exception as e:
#         response = Result(
#             message=str(e), status_code=3001, http_status_code=400
#         )
#         response.err_resp()


@bp.get('/tags/<svr_id>')
@auth_required(auth_token)
@bp.output(TagItem(many=True))
def list_svr_tags(svr_id):
    '''获取指定云服务器的用户Tags'''
    try:
        resource_ec2 = boto3.resource('ec2')
        thisSvr = resource_ec2.Instance(svr_id)
        userTags = [t for t in thisSvr.tags if t['Key'] not in ["Flag",]]
        response = Result(
            detail= userTags,
            status_code=200
            ) 
        return response.make_resp() 
    except Exception as ex:
        response = Result(
            message=str(ex), 
            status_code=3031, 
            http_status_code=400
        )
        response.err_resp()


@bp.put('/tags/<svr_id>')
@auth_required(auth_token)
@bp.input(TagItem)
# @bp.input(TagItem(many=True))
def mod_svr_tags(svr_id, parm):
    '''为指定云服务器新增/修改用户Tags'''
    try:
        # 禁止修改Flag tag
        # for tag in parm:
        #     if tag["Key"] == 'Flag':
        if parm["Key"] == 'Flag':
            raise ValueError('Flag tag unsupported')
        
        resource_ec2 = boto3.resource('ec2')
        thisSvr = resource_ec2.Instance(svr_id)
        newTags = thisSvr.create_tags(
            Tags=[parm]
        )
        userTags = [t for t in thisSvr.tags if t['Key'] != "Flag"]
        response = Result(
            detail= userTags,
            status_code=200
            ) 
        return response.make_resp() 
    except Exception as ex:
        response = Result(
            message=str(ex), 
            status_code=3032, 
            http_status_code=400
        )
        response.err_resp()


@bp.delete('/tags/<svr_id>')
@auth_required(auth_token)
@bp.input(TagItem)
def del_svr_tags(svr_id, parm):
    '''为指定云服务器删除用户Tags'''
    try:
        # 禁止删除Flag tag
        if parm["Key"] == 'Flag':
            raise ValueError('Flag tag unsupported')

        resource_ec2 = boto3.resource('ec2')
        thisSvr = resource_ec2.Instance(svr_id)
        delTags = thisSvr.delete_tags(
            Tags=[parm]
        )

        userTags = [t for t in thisSvr.tags if t['Key'] != "Flag"]
        response = Result(
            detail= userTags,
            status_code=200
            ) 
        return response.make_resp() 
    except Exception as ex:
        response = Result(
            message=str(ex), 
            status_code=3033, 
            http_status_code=400
        )
        response.err_resp()

