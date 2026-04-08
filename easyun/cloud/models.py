# -*- coding: utf-8 -*-
"""
  @module:  Cloud Provider Data Models
  @desc:    Unified data models for multi-cloud support.
            Provider 层返回这些 dataclass，API 层 Schema 做格式映射。
"""

from dataclasses import dataclass, field
from typing import Optional


# ── Compute ─────────────────────────────────────────────────────────

@dataclass
class ServerBrief:
    """服务器简要信息（列表用）"""
    id: str
    name: Optional[str]
    state: str
    instance_type: str
    az: Optional[str] = None


@dataclass
class ServerDetail(ServerBrief):
    """服务器详细信息"""
    vcpu: int = 0
    memory_gib: float = 0
    volume_size_gib: int = 0
    os_name: str = ''
    public_ip: Optional[str] = None
    private_ip: Optional[str] = None
    is_eip: bool = False


@dataclass
class ServerFullDetail:
    """服务器完整详情（详情页用）"""
    # property
    id: str
    name: Optional[str]
    instance_type: str
    vcpu: int
    memory_gib: float
    private_ip: Optional[str]
    public_ip: Optional[str]
    is_eip: bool
    state: str
    launch_time: str
    private_dns: Optional[str] = None
    public_dns: Optional[str] = None
    platform: str = ''
    virtualization: str = ''
    tenancy: str = 'default'
    usage_operation: str = ''
    monitoring: str = ''
    termination_protection: str = ''
    # image
    ami_id: str = ''
    ami_name: str = ''
    ami_path: str = ''
    arch: str = ''
    os_code: str = ''
    # access
    key_pair_name: str = ''
    iam_role: str = ''
    # associations
    volume_ids: list = field(default_factory=list)
    security_groups: list = field(default_factory=list)
    tags: list = field(default_factory=list)


@dataclass
class ImageInfo:
    """镜像信息"""
    id: str
    os_name: str
    os_version: str
    os_code: str
    description: str = ''
    root_device_path: str = ''
    root_device_type: str = ''
    root_device_disk: Optional[dict] = None


@dataclass
class InstanceTypeInfo:
    """实例规格信息"""
    instance_type: str
    family: str
    family_desc: str = ''
    vcpu: int = 0
    memory_gib: float = 0
    network_speed: str = ''
    monthly_price: Optional[float] = None


# ── Storage ─────────────────────────────────────────────────────────

@dataclass
class VolumeBrief:
    """卷简要信息"""
    id: str
    name: Optional[str]
    state: str
    az: str
    volume_type: str
    size_gib: int
    is_attachable: bool = False
    create_time: Optional[str] = None


@dataclass
class VolumeDetail(VolumeBrief):
    """卷详细信息"""
    iops: Optional[int] = None
    throughput: Optional[int] = None
    is_encrypted: bool = False
    is_multi_attach: bool = False
    attachments: list = field(default_factory=list)


@dataclass
class BucketBrief:
    """存储桶简要信息"""
    id: str
    region: str
    create_time: Optional[str] = None


@dataclass
class BucketDetail(BucketBrief):
    """存储桶详细信息"""
    url: str = ''
    access: Optional[dict] = None


# ── Network ─────────────────────────────────────────────────────────

@dataclass
class SubnetInfo:
    """子网信息"""
    id: str
    name: Optional[str]
    subnet_type: str  # public / private
    state: str
    vpc_id: str
    az: str
    cidr: str
    available_ips: int = 0
    is_map_public_ip: bool = False


@dataclass
class SecurityGroupInfo:
    """安全组信息"""
    id: str
    name: str
    description: str = ''
    vpc_id: str = ''


@dataclass
class StaticIpInfo:
    """静态 IP 信息"""
    id: str
    public_ip: str
    domain: str = ''
    association_id: Optional[str] = None
    association_target: Optional[str] = None


# ── Database ────────────────────────────────────────────────────────

@dataclass
class DBInstanceBrief:
    """数据库实例简要信息"""
    id: str
    engine: str
    engine_version: str = ''
    status: str = ''
    instance_class: str = ''
    az: str = ''
    multi_az: bool = False


@dataclass
class DBInstanceDetail(DBInstanceBrief):
    """数据库实例详细信息"""
    vcpu: int = 0
    memory_gib: float = 0
    storage_gib: int = 0
    endpoint: str = ''


# ── Load Balancer ───────────────────────────────────────────────────

@dataclass
class LoadBalancerBrief:
    """负载均衡简要信息"""
    id: str
    arn: str
    dns_name: str
    lb_type: str
    state: str
    scheme: str


@dataclass
class LoadBalancerDetail(LoadBalancerBrief):
    """负载均衡详细信息"""
    ip_type: str = ''
    azs: list = field(default_factory=list)
    security_groups: list = field(default_factory=list)
    create_time: Optional[str] = None


# ── Account ─────────────────────────────────────────────────────────

@dataclass
class RegionInfo:
    """区域信息"""
    code: str
    name: str
    country_code: str = ''


@dataclass
class QuotaInfo:
    """配额信息"""
    service_code: str
    quota_code: str
    quota_name: str
    value: float
    unit: str = ''


@dataclass
class KeyPairInfo:
    """密钥对信息"""
    name: str
    key_type: str
    fingerprint: str = ''
    tags: list = field(default_factory=list)
