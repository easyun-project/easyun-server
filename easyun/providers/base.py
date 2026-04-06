# -*- coding: utf-8 -*-
"""
  @module:  Cloud Provider Base
  @desc:    Abstract base classes for multi-cloud support.
"""

from abc import ABC, abstractmethod


# ── Provider & Account ──────────────────────────────────────────────

class CloudProvider(ABC):
    """云服务商抽象基类"""

    @abstractmethod
    def get_session(self, dc_name=None):
        ...

    @abstractmethod
    def get_client(self, service, **kwargs):
        ...

    @abstractmethod
    def get_resource(self, service, **kwargs):
        ...


class CloudAccountBase(ABC):
    """云账号级别操作（不绑定 region）"""

    @abstractmethod
    def list_regions(self) -> list:
        """列出可用区域"""
        ...

    @abstractmethod
    def get_quota(self, service_code, quota_code) -> dict:
        """查询服务配额"""
        ...

    @abstractmethod
    def get_pricing(self, service_code, **kwargs) -> dict:
        """查询定价"""
        ...


# ── Resource Base ───────────────────────────────────────────────────

class ResourceBase(ABC):
    """云资源通用基类"""

    @abstractmethod
    def get_detail(self) -> dict:
        ...

    @abstractmethod
    def get_tags(self) -> list:
        ...

    @abstractmethod
    def delete(self) -> dict:
        ...


# ── DataCenter ──────────────────────────────────────────────────────

class DataCenterBase(ResourceBase):
    """数据中心（虚拟网络）"""

    # 网络资源列表
    @abstractmethod
    def list_subnets(self) -> list:
        ...

    @abstractmethod
    def list_security_groups(self) -> list:
        ...

    @abstractmethod
    def list_route_tables(self) -> list:
        ...

    @abstractmethod
    def list_gateways(self) -> list:
        ...

    @abstractmethod
    def list_static_ips(self) -> list:
        ...

    @abstractmethod
    def get_cost_summary(self, period='monthly') -> dict:
        """获取费用汇总"""
        ...


# ── Network ─────────────────────────────────────────────────────────

class SubnetBase(ResourceBase):
    """子网"""

    @abstractmethod
    def get_subnet_type(self) -> str:
        """返回 'public' 或 'private'"""
        ...


class SecurityGroupBase(ResourceBase):
    """安全组"""

    @abstractmethod
    def add_rule(self, rule) -> dict:
        ...

    @abstractmethod
    def remove_rule(self, rule_id) -> dict:
        ...


# ── Compute ─────────────────────────────────────────────────────────

class ComputeInstanceBase(ResourceBase):
    """计算实例"""

    @abstractmethod
    def start(self) -> dict:
        ...

    @abstractmethod
    def stop(self) -> dict:
        ...

    @abstractmethod
    def reboot(self) -> dict:
        ...

    @classmethod
    @abstractmethod
    def list_images(cls, session, arch=None, os_type=None) -> list:
        """列出可用镜像"""
        ...

    @classmethod
    @abstractmethod
    def list_instance_types(cls, session, arch=None, family=None) -> list:
        """列出可用实例规格"""
        ...


# ── Storage ─────────────────────────────────────────────────────────

class StorageBucketBase(ResourceBase):
    """对象存储"""

    @abstractmethod
    def list_objects(self) -> list:
        ...


class StorageVolumeBase(ResourceBase):
    """块存储"""

    SYSTEM_DISK_PATHS = []  # 各 provider override

    @classmethod
    def get_disk_type(cls, attach_path):
        """根据挂载路径判断磁盘类型"""
        return 'system' if attach_path in cls.SYSTEM_DISK_PATHS else 'user'

    @abstractmethod
    def attach(self, instance_id, device) -> dict:
        ...

    @abstractmethod
    def detach(self) -> dict:
        ...


# ── Database ────────────────────────────────────────────────────────

class DatabaseInstanceBase(ResourceBase):
    """数据库实例"""
    pass


# ── Load Balancer ───────────────────────────────────────────────────

class LoadBalancerBase(ResourceBase):
    """负载均衡"""

    @abstractmethod
    def get_listeners(self) -> list:
        ...

    @abstractmethod
    def get_target_groups(self) -> list:
        ...
