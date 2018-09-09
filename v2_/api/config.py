# -*- coding: utf-8 -*-
"""
Created at: 18-1-5 下午1:26

@Author: Qian
"""

import hmac
import base64
import hashlib
from .my_time import get_timestamp
from .seller_info import ACCOUNT_INFO

"""
此文件是配置文件,包含向api发起请求所需要提供的信息
"""


class ListOrders:
    """
    `订单 API`中ListOrders部分。
    初始化 需提供 Account,  CreatedAfter或者LastUpdatedAfter的时间。
    """

    def __init__(self, Account, CreatedAfter=None, LastUpdatedAfter=None):
        try:
            self.__ACCOUNT_INFO = ACCOUNT_INFO[Account]
        except KeyError:
            raise Exception("No that account!")
        self.request_method = 'POST'
        self.max_requests = 6  # 最大请求限额
        self.recovery_time = 60  # 恢复速率每x秒一个请求
        self.url = 'https://mws.amazonservices.com/Orders/2013-09-01'
        self.payload = {'Action': 'ListOrders',
                        'Version': '2013-09-01',
                        'SellerId': self.__ACCOUNT_INFO['SellerId'],
                        'MarketplaceId.Id.1': self.__ACCOUNT_INFO['MarketplaceId.Id.1'],
                        'MarketplaceId.Id.2': self.__ACCOUNT_INFO['MarketplaceId.Id.2'],
                        'MarketplaceId.Id.3': self.__ACCOUNT_INFO['MarketplaceId.Id.3'],
                        'AWSAccessKeyId': self.__ACCOUNT_INFO['AWSAccessKeyId'],
                        'MWSAuthToken': self.__ACCOUNT_INFO['MWSAuthToken'],
                        'Timestamp': get_timestamp(),
                        'SignatureMethod': 'HmacSHA256',
                        'SignatureVersion': '2',
                        'Signature': None,
                        'CreatedAfter': CreatedAfter,
                        'LastUpdatedAfter': LastUpdatedAfter, }
        self.get_signature()

    def get_signature(self):
        assert (self.payload['CreatedAfter'] is not None) | (self.payload['LastUpdatedAfter'] is not None)
        if self.payload['CreatedAfter']:
            sign_string = "POST\nmws.amazonservices.com\n/Orders/2013-09-01\n" +\
                          "AWSAccessKeyId=%(AWSAccessKeyId)s" +\
                          "&Action=%(Action)s" +\
                          "&CreatedAfter=%(CreatedAfter)s" +\
                          "&MWSAuthToken=%(MWSAuthToken)s" +\
                          "&MarketplaceId.Id.1=%(MarketplaceId.Id.1)s" +\
                          "&MarketplaceId.Id.2=%(MarketplaceId.Id.2)s" +\
                          "&MarketplaceId.Id.3=%(MarketplaceId.Id.3)s" +\
                          "&SellerId=%(SellerId)s" +\
                          "&SignatureMethod=%(SignatureMethod)s" +\
                          "&SignatureVersion=%(SignatureVersion)s" +\
                          "&Timestamp=%(Timestamp)s" +\
                          "&Version=%(Version)s"
            self.payload.pop('LastUpdatedAfter')
        else:
            sign_string = "POST\nmws.amazonservices.com\n/Orders/2013-09-01\n" +\
                          "AWSAccessKeyId=%(AWSAccessKeyId)s" +\
                          "&Action=%(Action)s" +\
                          "&LastUpdatedAfter=%(LastUpdatedAfter)s" +\
                          "&MWSAuthToken=%(MWSAuthToken)s" +\
                          "&MarketplaceId.Id.1=%(MarketplaceId.Id.1)s" +\
                          "&MarketplaceId.Id.2=%(MarketplaceId.Id.2)s" +\
                          "&MarketplaceId.Id.3=%(MarketplaceId.Id.3)s" +\
                          "&SellerId=%(SellerId)s" +\
                          "&SignatureMethod=%(SignatureMethod)s" +\
                          "&SignatureVersion=%(SignatureVersion)s" +\
                          "&Timestamp=%(Timestamp)s" +\
                          "&Version=%(Version)s"
            self.payload.pop('CreatedAfter')
        sign_string = sign_string % self.payload
        sign_string = sign_string.replace(":", "%3A")
        # print(sign_string)
        dig = hmac.new(self.__ACCOUNT_INFO['key'], sign_string.encode(), digestmod=hashlib.sha256).digest()
        signature = base64.b64encode(dig).decode()
        # print(signature)
        self.payload['Signature'] = signature


class ListOrderItems:
    """
    `订单 API`中ListOrderItems部分。
    """

    def __init__(self, Account, AmazonOrderId):
        try:
            self.__ACCOUNT_INFO = ACCOUNT_INFO[Account]
        except KeyError:
            raise Exception("No that account!")
        self.request_method = 'POST'
        self.max_requests = 30  # 最大请求限额
        self.recovery_time = 2  # 恢复速率每x秒一个请求
        self.url = 'https://mws.amazonservices.com/Orders/2013-09-01'
        self.payload = {'Action': 'ListOrderItems',
                        'Version': '2013-09-01',
                        'SellerId': self.__ACCOUNT_INFO['SellerId'],
                        'AWSAccessKeyId': self.__ACCOUNT_INFO['AWSAccessKeyId'],
                        'MWSAuthToken': self.__ACCOUNT_INFO['MWSAuthToken'],
                        'Timestamp': get_timestamp(),
                        'AmazonOrderId': AmazonOrderId,
                        'SignatureMethod': 'HmacSHA256',
                        'SignatureVersion': '2',
                        'Signature': None, }
        self.get_signature()

    def get_signature(self):
        sign_string = "POST\nmws.amazonservices.com\n/Orders/2013-09-01\n" +\
                      "AWSAccessKeyId=%(AWSAccessKeyId)s" +\
                      "&Action=%(Action)s" +\
                      "&AmazonOrderId=%(AmazonOrderId)s" +\
                      "&MWSAuthToken=%(MWSAuthToken)s" +\
                      "&SellerId=%(SellerId)s" +\
                      "&SignatureMethod=%(SignatureMethod)s" +\
                      "&SignatureVersion=%(SignatureVersion)s" +\
                      "&Timestamp=%(Timestamp)s" +\
                      "&Version=%(Version)s"
        sign_string = sign_string % self.payload
        # 需要保证只有时间字符串中含有 : 符号 ！！！
        sign_string = sign_string.replace(":", "%3A")
        # print(sign_string)
        dig = hmac.new(self.__ACCOUNT_INFO['key'], sign_string.encode(), digestmod=hashlib.sha256).digest()
        signature = base64.b64encode(dig).decode()
        # print(signature)
        self.payload['Signature'] = signature


class ListInventorySupply:
    """
    `配送库存 API`中ListInventorySupply部分。
    """

    def __init__(self, Account, SKU):
        try:
            self.__ACCOUNT_INFO = ACCOUNT_INFO[Account]
        except KeyError:
            raise Exception("No that account!")
        self.request_method = 'POST'
        self.max_requests = 30  # 最大请求限额
        self.recovery_time = 0.5  # 恢复速率每x秒一个请求
        self.url = 'https://mws.amazonservices.com/FulfillmentInventory/2010-10-01'
        self.payload = {'Action': 'ListInventorySupply',
                        'Version': '2010-10-01',
                        'SellerId': self.__ACCOUNT_INFO['SellerId'],
                        'AWSAccessKeyId': self.__ACCOUNT_INFO['AWSAccessKeyId'],
                        'MWSAuthToken': self.__ACCOUNT_INFO['MWSAuthToken'],
                        'Timestamp': get_timestamp(),
                        'SignatureMethod': 'HmacSHA256',
                        'SignatureVersion': '2',
                        'Signature': None,
                        'SellerSkus.member.1': SKU, }
        self.get_signature()

    def get_signature(self):
        sign_string = "POST\nmws.amazonservices.com\n/FulfillmentInventory/2010-10-01\n" +\
                      "AWSAccessKeyId=%(AWSAccessKeyId)s" +\
                      "&Action=%(Action)s" +\
                      "&MWSAuthToken=%(MWSAuthToken)s" +\
                      "&SellerId=%(SellerId)s" +\
                      "&SellerSkus.member.1=%(SellerSkus.member.1)s" +\
                      "&SignatureMethod=%(SignatureMethod)s" +\
                      "&SignatureVersion=%(SignatureVersion)s" +\
                      "&Timestamp=%(Timestamp)s" +\
                      "&Version=%(Version)s"
        sign_string = sign_string % self.payload
        # 需要保证只有时间字符串中含有 : 符号 ！！！
        sign_string = sign_string.replace(":", "%3A")
        # print(sign_string)
        dig = hmac.new(self.__ACCOUNT_INFO['key'], sign_string.encode(), digestmod=hashlib.sha256).digest()
        signature = base64.b64encode(dig).decode()
        # print(signature)
        self.payload['Signature'] = signature


class RequestReport:
    """
    `报告 API`中RequestReport部分。
    """

    def __init__(self, Account, ReportType):
        try:
            self.__ACCOUNT_INFO = ACCOUNT_INFO[Account]
        except KeyError:
            raise Exception("No that account!")
        self.request_method = 'POST'
        self.max_requests = 15  # 最大请求限额
        self.recovery_time = 60  # 恢复速率每x秒一个请求
        self.url = 'https://mws.amazonservices.com/'
        self.payload = {'Action': 'RequestReport',
                        'Version': '2009-01-01',
                        'Merchant': self.__ACCOUNT_INFO['SellerId'],
                        'AWSAccessKeyId': self.__ACCOUNT_INFO['AWSAccessKeyId'],
                        'MWSAuthToken': self.__ACCOUNT_INFO['MWSAuthToken'],
                        'Timestamp': get_timestamp(),
                        'SignatureMethod': 'HmacSHA256',
                        'SignatureVersion': '2',
                        'Signature': None,
                        'ReportType': ReportType, }
        self.get_signature()

    def get_signature(self):
        sign_string = "POST\nmws.amazonservices.com\n/\n" \
                      "AWSAccessKeyId=%(AWSAccessKeyId)s" \
                      "&Action=%(Action)s" \
                      "&MWSAuthToken=%(MWSAuthToken)s" \
                      "&Merchant=%(Merchant)s" \
                      "&ReportType=%(ReportType)s" \
                      "&SignatureMethod=%(SignatureMethod)s" \
                      "&SignatureVersion=%(SignatureVersion)s" \
                      "&Timestamp=%(Timestamp)s" \
                      "&Version=%(Version)s"
        sign_string = sign_string % self.payload
        # 需要保证只有时间字符串中含有 : 符号 ！！！
        sign_string = sign_string.replace(":", "%3A")
        # print(sign_string)
        dig = hmac.new(self.__ACCOUNT_INFO['key'], sign_string.encode(), digestmod=hashlib.sha256).digest()
        signature = base64.b64encode(dig).decode()
        # print(signature)
        self.payload['Signature'] = signature


class GetReportRequestList:
    """
    `报告 API`中GetReportRequestList。
    """

    def __init__(self, Account, ReportRequestId):
        try:
            self.__ACCOUNT_INFO = ACCOUNT_INFO[Account]
        except KeyError:
            raise Exception("No that account!")
        self.request_method = 'POST'
        self.max_requests = 10  # 最大请求限额
        self.recovery_time = 45  # 恢复速率每x秒一个请求
        self.url = 'https://mws.amazonservices.com/'
        self.payload = {'Action': 'GetReportRequestList',
                        'Version': '2009-01-01',
                        'Merchant': self.__ACCOUNT_INFO['SellerId'],
                        'AWSAccessKeyId': self.__ACCOUNT_INFO['AWSAccessKeyId'],
                        'MWSAuthToken': self.__ACCOUNT_INFO['MWSAuthToken'],
                        'Timestamp': get_timestamp(),
                        'SignatureMethod': 'HmacSHA256',
                        'SignatureVersion': '2',
                        'Signature': None,
                        'ReportRequestIdList.Id.1': ReportRequestId}
        self.get_signature()

    def get_signature(self):
        sign_string = "POST\nmws.amazonservices.com\n/\n" \
                      "AWSAccessKeyId=%(AWSAccessKeyId)s" \
                      "&Action=%(Action)s" \
                      "&MWSAuthToken=%(MWSAuthToken)s" \
                      "&Merchant=%(Merchant)s" \
                      "&ReportRequestIdList.Id.1=%(ReportRequestIdList.Id.1)s" \
                      "&SignatureMethod=%(SignatureMethod)s" \
                      "&SignatureVersion=%(SignatureVersion)s" \
                      "&Timestamp=%(Timestamp)s" \
                      "&Version=%(Version)s"
        sign_string = sign_string % self.payload
        # 需要保证只有时间字符串中含有 : 符号 ！！！
        sign_string = sign_string.replace(":", "%3A")
        # print(sign_string)
        dig = hmac.new(self.__ACCOUNT_INFO['key'], sign_string.encode(), digestmod=hashlib.sha256).digest()
        signature = base64.b64encode(dig).decode()
        # print(signature)
        self.payload['Signature'] = signature


class GetReport:
    """
    `报告 API`中GetReport。
    """

    def __init__(self, Account, ReportId):
        try:
            self.__ACCOUNT_INFO = ACCOUNT_INFO[Account]
        except KeyError:
            raise Exception("No that account!")
        self.request_method = 'POST'
        self.max_requests = 15  # 最大请求限额
        self.recovery_time = 60  # 恢复速率每x秒一个请求
        self.url = 'https://mws.amazonservices.com/'
        self.payload = {'Action': 'GetReport',
                        'Version': '2009-01-01',
                        'Merchant': self.__ACCOUNT_INFO['SellerId'],
                        'AWSAccessKeyId': self.__ACCOUNT_INFO['AWSAccessKeyId'],
                        'MWSAuthToken': self.__ACCOUNT_INFO['MWSAuthToken'],
                        'Timestamp': get_timestamp(),
                        'SignatureMethod': 'HmacSHA256',
                        'SignatureVersion': '2',
                        'Signature': None,
                        'ReportId': ReportId}
        self.get_signature()

    def get_signature(self):
        sign_string = "POST\nmws.amazonservices.com\n/\n" \
                      "AWSAccessKeyId=%(AWSAccessKeyId)s" \
                      "&Action=%(Action)s" \
                      "&MWSAuthToken=%(MWSAuthToken)s" \
                      "&Merchant=%(Merchant)s" \
                      "&ReportId=%(ReportId)s" \
                      "&SignatureMethod=%(SignatureMethod)s" \
                      "&SignatureVersion=%(SignatureVersion)s" \
                      "&Timestamp=%(Timestamp)s" \
                      "&Version=%(Version)s"
        sign_string = sign_string % self.payload
        # 需要保证只有时间字符串中含有 : 符号 ！！！
        sign_string = sign_string.replace(":", "%3A")
        # print(sign_string)
        dig = hmac.new(self.__ACCOUNT_INFO['key'], sign_string.encode(), digestmod=hashlib.sha256).digest()
        signature = base64.b64encode(dig).decode()
        # print(signature)
        self.payload['Signature'] = signature



if __name__ == "__main__":
    pass
