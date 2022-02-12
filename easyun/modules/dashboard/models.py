# encoding: utf-8
"""
  @module:  Dashboard Models
  @desc:    Dashboard models define
  @author:  xdq
"""

import boto3


class Boto3_Cloudwatch:
    def __init__(self, region=boto3.session.Session().region_name):
        self._region = region
        self._client = boto3.client('cloudwatch', region_name=region)

    def get_alarms(self):
        alarms = {
            "iaNum": 0,
            "okNum": 0,
            "isNum": 0
        }

        alarm_map = {
            "OK": "okNum",
            "INSUFFICIENT_DATA": "isNum",
            "ALARM": "iaNum"
        }
        client = self._client
        res = client.describe_alarms()

        for alarm_type in res:
            for alarm in res[alarm_type]:
                if alarm_type in ["CompositeAlarms", "MetricAlarms"]:
                    set_value = alarm["StateValue"]
                    if set_value:
                        alarms[alarm_map[set_value]] += 1
        return alarms

    def get_dashboards(self):
        region = self._region
        client = self._client
        prefix_url = f"https://console.aws.amazon.com/cloudwatch/home?region={region}#dashboards:name="
        res = client.list_dashboards()
        dashboard_list = res["DashboardEntries"]
        dashboards = []
        for da in dashboard_list:
            name = da["DashboardName"]
            obj = {
                'title': name,
                'url': prefix_url + name
            }
            dashboards.append(obj)
        return dashboards


class Boto3_DynamoDB:
    def __init__(self, region_name='us-east-1'):
        self._resource = boto3.resource('dynamodb', region_name=region_name)
        self._client = boto3.client('dynamodb')

    def get_table_names(self):
        dynamodb_client = self._client
        table_name_list = dynamodb_client.list_tables()['TableNames']
        return table_name_list

    def get_summary_server(self):
        dynamodb_resource = self._resource
        db = dynamodb_resource.Table('Servers')
        summaries = db.scan()
        items = summaries['Items']
        return items

    def get_summary_s3(self):
        dynamodb_resource = self._resource
        db = dynamodb_resource.Table('Buckets')
        summaries = db.scan()
        items = summaries['Items']
        return items

    def get_summary_health(self):
        dynamodb_resource = self._resource
        db = dynamodb_resource.Table('Alarms')
        summaries = db.scan()
        items = summaries['Items']
        return items