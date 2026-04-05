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
        """获取云平台 session"""
        ...

    @abstractmethod
    def get_client(self, service, **kwargs):
        """获取服务 client"""
        ...

    @abstractmethod
    def get_resource(self, service, **kwargs):
        """获取服务 resource"""
        ...


class DataCenterBase(ABC):
    """数据中心（虚拟网络）抽象基类"""

    @abstractmethod
    def get_detail(self) -> dict:
        ...

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
    def delete(self) -> dict:
        ...


class SubnetBase(ABC):
    """子网抽象基类"""

    @abstractmethod
    def get_detail(self) -> dict:
        ...

    @abstractmethod
    def delete(self) -> dict:
        ...


class SecurityGroupBase(ABC):
    """安全组抽象基类"""

    @abstractmethod
    def get_detail(self) -> dict:
        ...

    @abstractmethod
    def delete(self) -> dict:
        ...


class ComputeInstanceBase(ABC):
    """计算实例抽象基类"""

    @abstractmethod
    def get_detail(self) -> dict:
        ...

    @abstractmethod
    def start(self) -> dict:
        ...

    @abstractmethod
    def stop(self) -> dict:
        ...

    @abstractmethod
    def delete(self) -> dict:
        ...


class StorageBucketBase(ABC):
    """对象存储抽象基类"""

    @abstractmethod
    def get_detail(self) -> dict:
        ...

    @abstractmethod
    def delete(self) -> dict:
        ...


class StorageVolumeBase(ABC):
    """块存储抽象基类"""

    @abstractmethod
    def get_detail(self) -> dict:
        ...

    @abstractmethod
    def attach(self, instance_id, device) -> dict:
        ...

    @abstractmethod
    def detach(self) -> dict:
        ...

    @abstractmethod
    def delete(self) -> dict:
        ...


class DatabaseInstanceBase(ABC):
    """数据库实例抽象基类"""

    @abstractmethod
    def get_detail(self) -> dict:
        ...

    @abstractmethod
    def delete(self) -> dict:
        ...


class LoadBalancerBase(ABC):
    """负载均衡抽象基类"""

    @abstractmethod
    def get_detail(self) -> dict:
        ...

    @abstractmethod
    def delete(self) -> dict:
        ...
