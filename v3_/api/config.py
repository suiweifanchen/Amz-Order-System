# -*- coding: utf-8 -*-
"""
Created at: 18-4-23 上午7:47

@Author: Qian
"""

import re
import hmac
import base64
import hashlib

from .my_time import get_timestamp

# add the father dir into the path
import sys
sys.path.append('..')

from exceptions import *

"""
此文件是配置文件,包含向api发起请求所需要提供的信息
"""

amazon_time_format = '^[-\d]{10}T[:\d]{8}Z$'


#################################################
# Amazon API 基类
class BaseConfig:

    # -------------------------------------------------
    def __init__(self, Account, *args, **kwargs):
        self._ACCOUNT_INFO = Account
        self.request_method = 'POST'
        self.max_requests = 30  # 最大请求限额
        self.recovery_time = 60  # 恢复速率每x秒一个请求
        self.url = 'https://mws.amazonservices.com/'
        self.payload = {'SellerId': self._ACCOUNT_INFO['SellerId'],
                        'AWSAccessKeyId': self._ACCOUNT_INFO['AWSAccessKeyId'],
                        'MWSAuthToken': self._ACCOUNT_INFO['MWSAuthToken'],
                        'Timestamp': get_timestamp(),
                        'SignatureMethod': 'HmacSHA256',
                        'SignatureVersion': '2',
                        'Signature': None, }
        self.sign_string = ""

    # -------------------------------------------------
    def get_signature(self):
        self.sign_string = self.sign_string % self.payload
        self.sign_string = self.sign_string.replace(":", "%3A").replace("#", "%23")
        # print(sign_string)
        dig = hmac.new(self._ACCOUNT_INFO['key'], self.sign_string.encode(), digestmod=hashlib.sha256).digest()
        signature = base64.b64encode(dig).decode()
        # print(signature)
        self.payload['Signature'] = signature


#################################################
# Orders API
class ListOrders(BaseConfig):
    """
    `订单 API`中ListOrders部分。
    初始化 需提供 Account,  CreatedAfter或者LastUpdatedAfter的时间。
    CreatedAfter与LastUpdatedAfter格式如：0000-00-00T00:00:00Z
    """

    # -------------------------------------------------
    def __init__(self, Account, CreatedAfter=None, LastUpdatedAfter=None, *args, **kwargs):
        if CreatedAfter:
            if not re.search(amazon_time_format, CreatedAfter):
                raise DatetimeError("Wrong datetime format, the format should be '0000-00-00T00:00:00Z'")
        elif LastUpdatedAfter:
            if not re.search(amazon_time_format, LastUpdatedAfter):
                raise DatetimeError("Wrong datetime format, the format should be '0000-00-00T00:00:00Z'")
        else:
            raise ArgsError("CreatedAfter or LastUpdatedAfter must be given")

        super(ListOrders, self).__init__(Account, *args, **kwargs)
        self.max_requests = 6  # 最大请求限额
        self.recovery_time = 60  # 恢复速率每x秒一个请求
        self.url = 'https://mws.amazonservices.com/Orders/2013-09-01'

        self.payload.update({'Action': 'ListOrders',
                             'Version': '2013-09-01',
                             'CreatedAfter': CreatedAfter,
                             'LastUpdatedAfter': LastUpdatedAfter,
                             'MarketplaceId.Id.1': self._ACCOUNT_INFO['MarketplaceId.Id.1'],
                             'MarketplaceId.Id.2': self._ACCOUNT_INFO['MarketplaceId.Id.2'],
                             'MarketplaceId.Id.3': self._ACCOUNT_INFO['MarketplaceId.Id.3'], })
        if self.payload['CreatedAfter']:
            self.sign_string = "POST\nmws.amazonservices.com\n/Orders/2013-09-01\n" \
                               "AWSAccessKeyId=%(AWSAccessKeyId)s" \
                               "&Action=%(Action)s" \
                               "&CreatedAfter=%(CreatedAfter)s" \
                               "&MWSAuthToken=%(MWSAuthToken)s" \
                               "&MarketplaceId.Id.1=%(MarketplaceId.Id.1)s" \
                               "&MarketplaceId.Id.2=%(MarketplaceId.Id.2)s" \
                               "&MarketplaceId.Id.3=%(MarketplaceId.Id.3)s" \
                               "&SellerId=%(SellerId)s" \
                               "&SignatureMethod=%(SignatureMethod)s" \
                               "&SignatureVersion=%(SignatureVersion)s" \
                               "&Timestamp=%(Timestamp)s" \
                               "&Version=%(Version)s"
            self.payload.pop('LastUpdatedAfter')
        else:
            self.sign_string = "POST\nmws.amazonservices.com\n/Orders/2013-09-01\n" \
                               "AWSAccessKeyId=%(AWSAccessKeyId)s" \
                               "&Action=%(Action)s" \
                               "&LastUpdatedAfter=%(LastUpdatedAfter)s" \
                               "&MWSAuthToken=%(MWSAuthToken)s" \
                               "&MarketplaceId.Id.1=%(MarketplaceId.Id.1)s" \
                               "&MarketplaceId.Id.2=%(MarketplaceId.Id.2)s" \
                               "&MarketplaceId.Id.3=%(MarketplaceId.Id.3)s" \
                               "&SellerId=%(SellerId)s" \
                               "&SignatureMethod=%(SignatureMethod)s" \
                               "&SignatureVersion=%(SignatureVersion)s" \
                               "&Timestamp=%(Timestamp)s" \
                               "&Version=%(Version)s"
            self.payload.pop('CreatedAfter')

        self.get_signature()


class ListOrderItems(BaseConfig):
    """
    `订单 API`中ListOrderItems部分。
    """

    # -------------------------------------------------
    def __init__(self, Account, AmazonOrderId, *args, **kwargs):
        super(ListOrderItems, self).__init__(Account, *args, **kwargs)
        self.max_requests = 30  # 最大请求限额
        self.recovery_time = 2  # 恢复速率每x秒一个请求
        self.url = 'https://mws.amazonservices.com/Orders/2013-09-01'

        self.payload.update({'Action': 'ListOrderItems',
                             'Version': '2013-09-01',
                             'AmazonOrderId': AmazonOrderId, })
        self.sign_string = "POST\nmws.amazonservices.com\n/Orders/2013-09-01\n" \
                           "AWSAccessKeyId=%(AWSAccessKeyId)s" \
                           "&Action=%(Action)s" \
                           "&AmazonOrderId=%(AmazonOrderId)s" \
                           "&MWSAuthToken=%(MWSAuthToken)s" \
                           "&SellerId=%(SellerId)s" \
                           "&SignatureMethod=%(SignatureMethod)s" \
                           "&SignatureVersion=%(SignatureVersion)s" \
                           "&Timestamp=%(Timestamp)s" \
                           "&Version=%(Version)s"

        self.get_signature()


#################################################
# FulfillmentInventory API
class ListInventorySupply(BaseConfig):
    """
    `配送库存 API`中ListInventorySupply部分。
    """

    # -------------------------------------------------
    def __init__(self, Account, MarketplaceId, SKU, *args, **kwargs):
        super(ListInventorySupply, self).__init__(Account, *args, **kwargs)
        self.max_requests = 30  # 最大请求限额
        self.recovery_time = 0.5  # 恢复速率每x秒一个请求
        self.url = 'https://mws.amazonservices.com/FulfillmentInventory/2010-10-01'

        self.payload.update({'Action': 'ListInventorySupply',
                             'Version': '2010-10-01',
                             'MarketplaceId': MarketplaceId,
                             'SellerSkus.member.1': SKU, })
        self.sign_string = "POST\nmws.amazonservices.com\n/FulfillmentInventory/2010-10-01\n" \
                           "AWSAccessKeyId=%(AWSAccessKeyId)s" \
                           "&Action=%(Action)s" \
                           "&MWSAuthToken=%(MWSAuthToken)s" \
                           "&MarketplaceId=%(MarketplaceId)s" \
                           "&SellerId=%(SellerId)s" \
                           "&SellerSkus.member.1=%(SellerSkus.member.1)s" \
                           "&SignatureMethod=%(SignatureMethod)s" \
                           "&SignatureVersion=%(SignatureVersion)s" \
                           "&Timestamp=%(Timestamp)s" \
                           "&Version=%(Version)s"

        self.get_signature()


#################################################
# Report API
class RequestReport(BaseConfig):
    """
    `报告 API`中RequestReport部分。
    """

    # -------------------------------------------------
    def __init__(self, Account, MarketplaceId, ReportType, *args, **kwargs):
        super(RequestReport, self).__init__(Account, *args, **kwargs)
        self.max_requests = 15  # 最大请求限额
        self.recovery_time = 60  # 恢复速率每x秒一个请求
        self.url = 'https://mws.amazonservices.com/'

        self.payload.update({'Action': 'RequestReport',
                             'Version': '2009-01-01',
                             'Merchant': self.payload.pop('SellerId'),
                             'MarketplaceIdList.Id.1': MarketplaceId,
                             'ReportType': ReportType, })
        self.sign_string = "POST\nmws.amazonservices.com\n/\n" \
                           "AWSAccessKeyId=%(AWSAccessKeyId)s" \
                           "&Action=%(Action)s" \
                           "&MWSAuthToken=%(MWSAuthToken)s" \
                           "&MarketplaceIdList.Id.1=%(MarketplaceIdList.Id.1)s" \
                           "&Merchant=%(Merchant)s" \
                           "&ReportType=%(ReportType)s" \
                           "&SignatureMethod=%(SignatureMethod)s" \
                           "&SignatureVersion=%(SignatureVersion)s" \
                           "&Timestamp=%(Timestamp)s" \
                           "&Version=%(Version)s"

        self.get_signature()


class GetReportRequestList(BaseConfig):
    """
    `报告 API`中GetReportRequestList。
    """

    # -------------------------------------------------
    def __init__(self, Account, ReportRequestId, *args, **kwargs):
        super(GetReportRequestList, self).__init__(Account, *args, **kwargs)
        self.max_requests = 10  # 最大请求限额
        self.recovery_time = 45  # 恢复速率每x秒一个请求
        self.url = 'https://mws.amazonservices.com/'

        self.payload.update({'Action': 'GetReportRequestList',
                             'Version': '2009-01-01',
                             'Merchant': self.payload.pop('SellerId'),
                             'ReportRequestIdList.Id.1': ReportRequestId, })
        self.sign_string = "POST\nmws.amazonservices.com\n/\n" \
                           "AWSAccessKeyId=%(AWSAccessKeyId)s" \
                           "&Action=%(Action)s" \
                           "&MWSAuthToken=%(MWSAuthToken)s" \
                           "&Merchant=%(Merchant)s" \
                           "&ReportRequestIdList.Id.1=%(ReportRequestIdList.Id.1)s" \
                           "&SignatureMethod=%(SignatureMethod)s" \
                           "&SignatureVersion=%(SignatureVersion)s" \
                           "&Timestamp=%(Timestamp)s" \
                           "&Version=%(Version)s"

        self.get_signature()


class GetReport(BaseConfig):
    """
    `报告 API`中GetReport。
    """

    # -------------------------------------------------
    def __init__(self, Account, ReportId, *args, **kwargs):
        super(GetReport, self).__init__(Account, *args, **kwargs)
        self.max_requests = 15  # 最大请求限额
        self.recovery_time = 60  # 恢复速率每x秒一个请求
        self.url = 'https://mws.amazonservices.com/'

        self.payload.update({'Action': 'GetReport',
                             'Version': '2009-01-01',
                             'Merchant': self.payload.pop('SellerId'),
                             'ReportId': ReportId, })
        self.sign_string = "POST\nmws.amazonservices.com\n/\n" \
                           "AWSAccessKeyId=%(AWSAccessKeyId)s" \
                           "&Action=%(Action)s" \
                           "&MWSAuthToken=%(MWSAuthToken)s" \
                           "&Merchant=%(Merchant)s" \
                           "&ReportId=%(ReportId)s" \
                           "&SignatureMethod=%(SignatureMethod)s" \
                           "&SignatureVersion=%(SignatureVersion)s" \
                           "&Timestamp=%(Timestamp)s" \
                           "&Version=%(Version)s"

        self.get_signature()


#################################################
# Products API
class GetMyPriceForSKU(BaseConfig):
    """
    `商品 API`中GetMyPriceForSKU。
    """

    # -------------------------------------------------
    def __init__(self, Account, MarketplaceId, SKU, *args, **kwargs):
        super(GetMyPriceForSKU, self).__init__(Account, *args, **kwargs)
        self.max_requests = 20  # 最大请求限额
        self.recovery_time = 0.1  # 恢复速率每x秒一个请求
        self.url = "https://mws.amazonservices.com/Products/2011-10-01"

        self.payload.update({'Action': 'GetMyPriceForSKU',
                             'Version': '2011-10-01',
                             'MarketplaceId': MarketplaceId,
                             'SellerSKUList.SellerSKU.1': SKU, })
        self.sign_string = "POST\nmws.amazonservices.com\n/Products/2011-10-01\n" \
                           "AWSAccessKeyId=%(AWSAccessKeyId)s" \
                           "&Action=%(Action)s" \
                           "&MWSAuthToken=%(MWSAuthToken)s" \
                           "&MarketplaceId=%(MarketplaceId)s" \
                           "&SellerId=%(SellerId)s" \
                           "&SellerSKUList.SellerSKU.1=%(SellerSKUList.SellerSKU.1)s" \
                           "&SignatureMethod=%(SignatureMethod)s" \
                           "&SignatureVersion=%(SignatureVersion)s" \
                           "&Timestamp=%(Timestamp)s" \
                           "&Version=%(Version)s"

        self.get_signature()


if __name__ == '__main__':
    pass
