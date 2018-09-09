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
            self.ACCOUNT_INFO = ACCOUNT_INFO[Account]
        except KeyError:
            raise Exception("No that account!")
        self.request_method = 'POST'
        self.max_requests = 6  # 最大请求限额
        self.recovery_time = 60  # 恢复速率每x秒一个请求
        self.url = 'https://mws.amazonservices.com/Orders/2013-09-01'
        self.payload = {'Action': 'ListOrders',
                        'Version': '2013-09-01',
                        'SellerId': self.ACCOUNT_INFO['SellerId'],
                        'MarketplaceId.Id.1': self.ACCOUNT_INFO['MarketplaceId.Id.1'],
                        'MarketplaceId.Id.2': self.ACCOUNT_INFO['MarketplaceId.Id.2'],
                        'MarketplaceId.Id.3': self.ACCOUNT_INFO['MarketplaceId.Id.3'],
                        'AWSAccessKeyId': self.ACCOUNT_INFO['AWSAccessKeyId'],
                        'MWSAuthToken': self.ACCOUNT_INFO['MWSAuthToken'],
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
        dig = hmac.new(self.ACCOUNT_INFO['key'], sign_string.encode(), digestmod=hashlib.sha256).digest()
        signature = base64.b64encode(dig).decode()
        # print(signature)
        self.payload['Signature'] = signature


class ListOrderItems:
    """
    `订单 API`中ListOrderItems部分。
    """

    def __init__(self, Account, AmazonOrderId):
        try:
            self.ACCOUNT_INFO = ACCOUNT_INFO[Account]
        except KeyError:
            raise Exception("No that account!")
        self.request_method = 'POST'
        self.max_requests = 30  # 最大请求限额
        self.recovery_time = 2  # 恢复速率每x秒一个请求
        self.url = 'https://mws.amazonservices.com/Orders/2013-09-01'
        self.payload = {'Action': 'ListOrderItems',
                        'Version': '2013-09-01',
                        'SellerId': self.ACCOUNT_INFO['SellerId'],
                        'AWSAccessKeyId': self.ACCOUNT_INFO['AWSAccessKeyId'],
                        'MWSAuthToken': self.ACCOUNT_INFO['MWSAuthToken'],
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
        dig = hmac.new(self.ACCOUNT_INFO['key'], sign_string.encode(), digestmod=hashlib.sha256).digest()
        signature = base64.b64encode(dig).decode()
        # print(signature)
        self.payload['Signature'] = signature


if __name__ == "__main__":
    pass
