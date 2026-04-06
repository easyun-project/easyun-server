# -*- coding: utf-8 -*-
"""
  @module:  Database SDK Module
  @desc:    AWS SDK Boto3 Database(RDS) Client and Resource Wrapper.
"""

from botocore.exceptions import ClientError
from ...session import get_easyun_session


from easyun.providers.base import DatabaseInstanceBase

class DBInstance(DatabaseInstanceBase):
    def __init__(self, dbi_id, dc_name=None):
        self.id = dbi_id
        session = get_easyun_session(dc_name)
        self._client = session.client('rds')
        try:
            self.dbiDict = self._client.describe_db_instances(
                DBInstanceIdentifier=[self.id]
            )['DBInstances'][0]
            self.tagName = next(
                (tag['Value'] for tag in self.dbiDict['TagList'] if tag["Key"] == 'Name'), None
            )
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_detail(self):
        '''get db instance's detail info'''
        dbi = self.dbiDict
        try:
            userTags = [tag for tag in dbi['TagList'] if tag["Key"] not in ['Flag', 'Name']]
            dbiItem = {
                'dbiId': dbi['DBInstanceIdentifier'],
                'tagName': self.tagName,
                'dbiEngine': dbi['Engine'],
                'engineVer': dbi['EngineVersion'],
                'dbiStatus': 'available',
                'dbiSize': dbi['DBInstanceClass'],
                'vcpuNum': 1,
                'ramSize': 2,
                'volumeSize': 20,
                'dbiAz': dbi['AvailabilityZone'],
                'multiAz': dbi['MultiAZ'],
                'dbiEndpoint': dbi['Endpoint'].get('Address'),
                'createTime': dbi['InstanceCreateTime'].isoformat(),
                'userTags': userTags
            }
            return dbiItem
        except Exception as ex:
            return '%s: %s' % (self.__class__.__name__, ex)

    def get_tags(self):
        try:
            return [t for t in self.dbiDict.get("TagList", []) if t["Key"] not in ["Flag"]]
        except Exception:
            return []

    def delete(self):
        '''delete the db instance'''
        try:
            resp = self._client.delete_db_instance(
                DBInstanceIdentifier=self.id,
                SkipFinalSnapshot=True,
            )
            return {'dbiId': self.id, 'status': resp['DBInstance']['DBInstanceStatus']}
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))
