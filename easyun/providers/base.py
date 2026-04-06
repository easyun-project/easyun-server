# -*- coding: utf-8 -*-
"""
  @module:  Cloud Provider Base
  @desc:    Abstract base classes for multi-cloud support.
"""

from abc import ABC, abstractmethod


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


class DataCenterBase(ResourceBase):
    """数据中心（虚拟网络）"""

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


class SubnetBase(ResourceBase):
    """子网"""
    pass


class SecurityGroupBase(ResourceBase):
    """安全组"""

    @abstractmethod
    def add_rule(self, rule) -> dict:
        ...

    @abstractmethod
    def remove_rule(self, rule_id) -> dict:
        ...


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


class StorageBucketBase(ResourceBase):
    """对象存储"""

    @abstractmethod
    def list_objects(self) -> list:
        ...


class StorageVolumeBase(ResourceBase):
    """块存储"""

    @abstractmethod
    def attach(self, instance_id, device) -> dict:
        ...

    @abstractmethod
    def detach(self) -> dict:
        ...


class DatabaseInstanceBase(ResourceBase):
    """数据库实例"""
    pass


class LoadBalancerBase(ResourceBase):
    """负载均衡"""

    @abstractmethod
    def get_listeners(self) -> list:
        ...

    @abstractmethod
    def get_target_groups(self) -> list:
        ...
