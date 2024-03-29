# -*- coding: utf-8 -*-
"""
  @module:  The API Wrapper Module
  @desc:    AWS SDK Boto3 Client and Resource Wrapper.  
  @auth:    
"""
import boto3
import calendar
from datetime import datetime, date, timedelta


# SDK: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ce.html
class CostExplorer(object):
    def __init__(self, dc_name, region='us-east-1'):
        self._client = boto3.client('ce', region_name=region)
        self.filterTag = {'Key': 'Flag', 'Values': [dc_name]}
        self._metrics = ['UnblendedCost', 'UsageQuantity']

    # CostExplorer.Client.get_cost_and_usage
    def get_total_cost(self, start_date, end_date, time_cycle='MONTHLY'):
        '''get total cost in a time cycle'''
        try:
            # start_date = '2022-03-01'
            # end_date = '2022-04-01'
            totalList = []
            kwargs = {
                'TimePeriod': {'Start': start_date, 'End': end_date},
                'Metrics': self._metrics,
                'Granularity': time_cycle,
            }
            while True:
                getResp = self._client.get_cost_and_usage(
                    **kwargs,
                    Filter={
                        "Tags": self.filterTag,
                        # "Dimensions": {"Key": "REGION", "Values": [ "us-west-1" ]}
                    },
                )
                for r in getResp['ResultsByTime']:
                    ttlcost = r.get('Total', {}).get(self._metrics[0], {})
                    tmpItem = {
                        'timePeriod': r.get('TimePeriod', {}),
                        'totalCost': {
                            'value': ttlcost.get('Amount'),
                            'unit': ttlcost.get('Unit'),
                            'metric': self._metrics[0],
                        },
                    }
                    totalList.append(tmpItem)
                if 'NextToken' not in getResp:
                    break
                kwargs['NextToken'] = getResp['NextToken']
            return totalList

        except Exception as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_monthly_total_cost(self, month=None):
        '''get total cost in a month'''
        # month = '2021-03'
        try:
            if month is None:
                lastDate = date.today()
                firtDate = lastDate.replace(day=1)
            else:
                firtDate = datetime.strptime(month, '%Y-%m').date()
                monthLength = calendar.monthrange(firtDate.year, firtDate.month)[1]
                lastDate = firtDate + timedelta(monthLength)

            start_date = firtDate.strftime('%Y-%m-%d')
            end_date = lastDate.strftime('%Y-%m-%d')

            totalList = self.get_total_cost(start_date, end_date, 'MONTHLY')
            return totalList[0] if totalList else {}

        except Exception as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_day_total_cost(self, tdate=None):
        '''get one day total cost'''
        # tdate = '2021-02-03'
        try:
            if tdate is None:
                todayDate = date.today()
            else:
                todayDate = datetime.strptime(tdate, '%Y-%m-%d').date()
            yesterdayDate = todayDate - timedelta(days=1)

            start_date = yesterdayDate.strftime('%Y-%m-%d')
            end_date = todayDate.strftime('%Y-%m-%d')

            totalList = self.get_total_cost(start_date, end_date, 'DAILY')
            return totalList[0] if totalList else {}

        except Exception as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_latest_week_daily_cost(self):
        '''get daily total cost in latest week'''
        try:
            todayDate = date.today()
            beforeDate = todayDate - timedelta(days=7)

            start_date = beforeDate.strftime('%Y-%m-%d')
            end_date = todayDate.strftime('%Y-%m-%d')

            totalList = self.get_total_cost(start_date, end_date, 'DAILY')
            return totalList

        except Exception as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_monthly_cost_list(self, start_month, end_month):
        '''get monthly cost and usage group by service'''
        try:
            firtDate = datetime.strptime(start_month, '%Y-%m').date()
            secondDate = datetime.strptime(end_month, '%Y-%m').date()
            # get end month's next month 1st day
            monthLength = calendar.monthrange(secondDate.year, secondDate.month)[1]
            lastDate = secondDate + timedelta(monthLength)

            start_date = firtDate.strftime('%Y-%m-%d')
            end_date = lastDate.strftime('%Y-%m-%d')

            costList = []
            kwargs = {
                'TimePeriod': {'Start': start_date, 'End': end_date},
                'Metrics': self._metrics,
                'Granularity': 'MONTHLY',
            }
            while True:
                getResp = self._client.get_cost_and_usage(
                    **kwargs,
                    Filter={
                        "Tags": self.filterTag,
                    },
                    GroupBy=[
                        {'Type': 'DIMENSION', 'Key': 'SERVICE'},
                        # {'Type': 'DIMENSION', 'Key': 'REGION'},
                    ],
                )
                for r in getResp['ResultsByTime']:
                    ttlcost = r.get('Total', {}).get(self._metrics[0], {})
                    groupList = []
                    for g in r['Groups']:
                        service = g.get('Keys', [])[0]
                        cost = g.get('Metrics', {}).get(self._metrics[0], {})
                        usage = g.get('Metrics', {}).get(self._metrics[1], {})
                        svcItem = {
                            'service': service,
                            'usage': {
                                'value': usage.get('Amount'),
                                'unit': usage.get('Unit'),
                                'metric': self._metrics[1],
                            },
                            'cost': {
                                'value': cost.get('Amount'),
                                'unit': cost.get('Unit'),
                                'metric': self._metrics[0],
                            },
                        }
                        groupList.append(svcItem)
                    tmpItem = {
                        'timePeriod': r.get('TimePeriod', {}),
                        'totalCost': {
                            'value': ttlcost.get('Amount'),
                            'unit': ttlcost.get('Unit'),
                            'metric': self._metrics[0],
                        },
                        'groupCost': groupList,
                    }
                    costList.append(tmpItem)
                if 'NextToken' not in getResp:
                    break
                kwargs['NextToken'] = getResp['NextToken']
            return costList

        except Exception as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_a_month_cost_list(self, month=None):
        '''get monthly cost and usage group by service'''
        try:
            if month is None:
                start_month = date.today().strftime('%Y-%m')
                end_month = start_month
            else:
                start_month = month
                end_month = month

            costList = self.get_monthly_cost_list(start_month, end_month)
            return costList[0] if costList else {}

        except Exception as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    # CostExplorer.Client.get_cost_forecast
    def get_forecast_total_cost(self, month=None, time_cycle='MONTHLY'):
        '''get forecast cost in future(month)'''
        try:
            todayDate = date.today()
            firtDate = todayDate.replace(day=1)
            monthLength = calendar.monthrange(firtDate.year, firtDate.month)[1]
            lastDate = firtDate + timedelta(monthLength)

            start_date = todayDate.strftime('%Y-%m-%d')
            end_date = lastDate.strftime('%Y-%m-%d')

            resp = self._client.get_cost_forecast(
                TimePeriod={'Start': start_date, 'End': end_date},
                Metric='UNBLENDED_COST',
                Granularity=time_cycle,
                Filter={
                    "Tags": self.filterTag,
                },
            )
            unit = resp['Total'].get('Unit')
            # 暂时只考虑一个周期的预测
            fcResp = resp['ForecastResultsByTime'][0]
            foreCast = {
                'timePeriod': fcResp.get('TimePeriod', {}),
                'totalCost': {
                    'value': fcResp.get('MeanValue'),
                    'unit': unit,
                    'metric': self._metrics[0],
                },
            }
            return foreCast
        # 如果数据不足以预测则通过按天数比例预估整月花费
        except self._client.exceptions.DataUnavailableException:
            currCost = self.get_monthly_total_cost()
            value = float(currCost['totalCost'].get('value'))
            currCost['totalCost']['value'] = str(value * monthLength / todayDate.day)
            currCost['timePeriod']['End'] = end_date

            return currCost
        except Exception as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))


'''
AWS API Service endpoint
'''
# The Cost Explorer API provides the following endpoint:
# Global Region：
# https://ce.us-east-1.amazonaws.com
# GCR Region:
# https://ce.cn-northwest-1.amazonaws.com.cn


def get_ce_region(account_type):
    if account_type == 'global':
        ceRegion = 'us-east-1'
    elif account_type == 'gcr':
        ceRegion = 'cn-northwest-1'
    else:
        ceRegion = None
    return ceRegion
