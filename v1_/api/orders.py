# -*- coding: utf-8 -*-
"""
Created at: 18-1-4 下午2:58

@Author: Qian
"""

import re
import pymysql
import requests
from my_modules import mysqlconn
from xml.etree import ElementTree as ET

from . import config as uc  # user_config 缩写
from .my_time import get_utc_time

keys = ['LatestShipDate', 'OrderType', 'PurchaseDate', 'AmazonOrderId',
        'BuyerEmail', 'IsReplacementOrder', 'LastUpdateDate',
        'NumberOfItemsShipped', 'ShipServiceLevel', 'OrderStatus',
        'SalesChannel', 'ShippedByAmazonTFM', 'IsBusinessOrder',
        'LatestDeliveryDate', 'NumberOfItemsUnshipped', 'PaymentMethodDetail',
        'BuyerName', 'EarliestDeliveryDate', 'CurrencyCode',
        'Amount', 'IsPremiumOrder', 'EarliestShipDate', 'MarketplaceId',
        'FulfillmentChannel', 'PaymentMethod', 'City',
        'AddressType', 'PostalCode', 'StateOrRegion', 'Phone', 'CountryCode',
        'Name', 'AddressLine1', 'IsPrime', 'ShipmentServiceLevelCategory']


def parse_to_dict(node, info_dict=None):
    """递归遍历node节点(ET解析xml的节点)下所有信息
    将{tag:text}键值对存入info_dict字典中
    使用示例：
    >>> root = ET.parse("file.xml").getroot()
    >>> info_dict = parse_to_dict(root)
    >>> info_dict
    {node1.tag: node1.text,
     node2.tag: {sub_node2.tag: sub_node2.text},
     node3.tag: node1.text,}
    """

    if not info_dict:
        info_dict = {}
    for child in node:
        if child.getchildren():
            info_dict[child.tag] = parse_to_dict(child)
        else:
            info_dict[child.tag] = child.text
    return info_dict


def flat_dict(orig_dict):
    """将多层字典扁平化，删除上层key
    即
    >>> d = {'a': {'b': 1, 'c': 2}, 'd':3}
    >>> d = flat_dict(d)
    >>> d
    {'b': 1, 'c': 2, 'd':3}
    """

    new_dict = {}
    for key in orig_dict:
        if isinstance(orig_dict[key], dict):
            new_dict.update(flat_dict(orig_dict[key]))
        else:
            new_dict[key] = orig_dict[key]
    return new_dict


def format_data(data):
    """格式化order_info里的数据：
    1. 将时间数据中的'T', 'Z'字符删除
    2. 将1970-01-01 00:00:00替换成0000-00-00 00:00:00
    3. 只取需要的信息
    """

    d = {}
    keys = ['AmazonOrderId', 'LastUpdateDate', 'ASIN',
            'SellerSKU', 'PaidDate', 'LatestShipDate',
            'OrderType', 'PurchaseDate', 'BuyerEmail',
            'IsReplacementOrder', 'NumberOfItemsShipped', 'ShipServiceLevel',
            'OrderStatus', 'SalesChannel', 'ShippedByAmazonTFM',
            'IsBusinessOrder', 'LatestDeliveryDate', 'NumberOfItemsUnshipped',
            'PaymentMethodDetail', 'BuyerName', 'EarliestDeliveryDate',
            'CurrencyCode', 'Amount', 'IsPremiumOrder',
            'EarliestShipDate', 'MarketplaceId', 'FulfillmentChannel',
            'PurchaseOrderNumber',
            'PaymentMethod', 'City', 'AddressType',
            'PostalCode', 'StateOrRegion', 'Phone',
            'CountryCode', 'Name', 'AddressLine1',
            'AddressLine2', 'IsPrime', 'ShipmentServiceLevelCategory',
            'SellerOrderId', 'Seller', 'RequestId_1',
            'RequestId_2']

    # 时间字符串的正则表达式
    string = '^[-\d]{10}T[:\d]{8}Z$'
    for key in keys:
        if data.get(key):
            if re.search(string, data[key]):
                data[key] = re.sub('[TZ]', ' ', data[key]).strip()
            if data[key] == "1970-01-01 00:00:00":
                data[key] = "0000-00-00 00:00:00"
            d[key] = data[key]
    return d


def get_order_items(account, order_id):
    """根据order_id使用api请求订单包含的商品"""

    lot = uc.ListOrderItems(account, order_id)
    page = requests.post(lot.url, data=lot.payload)
    root = ET.fromstring(page.text.replace(' xmlns="https://mws.amazonservices.com/Orders/2013-09-01"', ''))
    request_id = root.find('ResponseMetadata').find('RequestId').text
    order_items = root.find('ListOrderItemsResult').find('OrderItems').findall('OrderItem')
    items_list = []
    for order_item in order_items:
        item_info = parse_to_dict(order_item)
        item_info = flat_dict(item_info)
        item_info['RequestId_2'] = request_id
        items_list.append(item_info)
    return tuple(items_list)


def get_cr_orders(account, created_after="0000-00-00 00:00:00", tz='UTC+8'):
    """获取CreateAfter之后的订单
    CreateAfter未给定或者为"0000-00-00 00:00:00"，则默认为utc当前时间
    CreateAfter给定，，则根据所在时区tz,会自动转成UTC时间
    tz指参数CreateAfter时间所在的时区
    """

    # 初始化CreateAfter的值
    if created_after == "0000-00-00 00:00:00":
        created_after = get_utc_time()
    else:
        created_after = get_utc_time(created_after, tz)

    # 获取订单信息
    lo = uc.ListOrders(Account=account, CreatedAfter=created_after)
    if lo.request_method == 'POST':
        page = requests.post(lo.url, data=lo.payload)
    else:
        raise Exception(lo.request_method)

    # 解析订单信息（xml字符串）
    root = ET.fromstring(page.text.replace(' xmlns="https://mws.amazonservices.com/Orders/2013-09-01"', ''))
    # next_token = root.find('ListOrdersResult').find('NextToken')
    request_id = root.find('ResponseMetadata').find('RequestId').text
    orders = root.find('ListOrdersResult').find('Orders').findall('Order')

    conn = mysqlconn.mysqlconn()
    cur = conn.cursor()
    for order in orders:
        # 循环处理订单
        # 1. 首先判断订单状态,如果是Pending状态,PaidDate为"0000-00-00 00:00:00"
        #                  如果不是Pending状态.若数据库里有该订单的PaidDate,则用数据库中的PaidDate
        #                                    若数据库里没有该订单的PaidDate,则用此次请求结果中的LastUpdateDate代替
        # 2. 如果数据库里有该订单的信息,说明不是新订单,不需要再去请求订单所包含的商品,直接用数据库中的数据
        #    否则需要。
        order_info = parse_to_dict(order)
        order_info = flat_dict(order_info)
        order_info = format_data(order_info)
        order_info['RequestId_1'] = request_id
        # 将卖家名称加入进去
        order_info["Seller"] = account

        # 选出AmazonOrderId和ASIN的最新的记录
        newest_record = "select * from amazon_orders as a where not exists" +\
                        "(select 1 from amazon_orders as b where b.AmazonOrderId=a.AmazonOrderId " +\
                        "and b.ASIN=a.ASIN and b.LastUpdateDate>a.LastUpdateDate)"
        sql = "select * from (%s) as t where t.AmazonOrderId='%s'" % (newest_record, order_info['AmazonOrderId'])
        cur.execute(sql)
        data = cur.fetchall()

        # 如果此次请求结果中的LastUpdateDate约数据库中的一样,说明已在数据库中记录，不用做任何处理
        if data and str(data[0][1]) == order_info['LastUpdateDate']:
            continue

        # 处理PaidDate
        if order_info['OrderStatus'] == 'Pending':
            order_info['PaidDate'] = "0000-00-00 00:00:00"
        else:
            # 如果数据库里有该订单的PaidDate,则用数据库中的PaidDate,否则用此次请求结果中的LastUpdateDate
            if data and (data[0][4] is not None):
                order_info['PaidDate'] = str(data[0][4])
            else:
                order_info['PaidDate'] = order_info['LastUpdateDate']

        # 如果数据库里有该订单的信息,说明不是新订单,不需要再去请求订单所包含的商品,否则需要。
        if data:
            for i in range(len(data)):
                order_info_cp = order_info.copy()
                order_info_cp['ASIN'] = data[i][2]
                order_info_cp['SellerSKU'] = data[i][3]
                order_info_cp['RequestId_2'] = data[i][41]
                try:
                    # 更新到数据库
                    mysqlconn.db_insert(conn, order_info_cp, 'amazon_orders')
                except pymysql.err.IntegrityError:
                    pass
        else:
            # 请求订单所包含的商品信息
            order_items = get_order_items(account, order_info['AmazonOrderId'])
            for i in range(len(order_items)):
                order_info_cp = order_info.copy()
                order_info_cp['ASIN'] = order_items[i]['ASIN']
                order_info_cp['SellerSKU'] = order_items[i]['SellerSKU']
                order_info_cp['RequestId_2'] = order_items[i]['RequestId_2']
                try:
                    # 更新到数据库
                    mysqlconn.db_insert(conn, order_info_cp, 'amazon_orders')
                except pymysql.err.IntegrityError:
                    pass
    conn.close()


def get_lu_orders(account, last_updated_after="0000-00-00 00:00:00", tz='UTC+8'):
    """获取CreateAfter之后的订单
    last_updated_after未给定或者为"0000-00-00 00:00:00"，则默认为utc当前时间
    last_updated_after给定，则根据所在时区tz,会自动转成UTC时间
    tz指参数last_updated_after时间所在的时区
    """

    # 初始化CreateAfter的值
    if last_updated_after == "0000-00-00 00:00:00":
        last_updated_after = get_utc_time()
    else:
        last_updated_after = get_utc_time(last_updated_after, tz)

    # 获取订单信息
    lo = uc.ListOrders(Account=account, LastUpdatedAfter=last_updated_after)
    if lo.request_method == 'POST':
        page = requests.post(lo.url, data=lo.payload)
    else:
        raise Exception(lo.request_method)

    # 解析订单信息（xml字符串）
    root = ET.fromstring(page.text.replace(' xmlns="https://mws.amazonservices.com/Orders/2013-09-01"', ''))
    # next_token = root.find('ListOrdersResult').find('NextToken')
    request_id = root.find('ResponseMetadata').find('RequestId').text
    orders = root.find('ListOrdersResult').find('Orders').findall('Order')

    conn = mysqlconn.mysqlconn()
    cur = conn.cursor()
    for order in orders:
        order_info = parse_to_dict(order)
        order_info = flat_dict(order_info)
        order_info = format_data(order_info)
        order_info['RequestId_1'] = request_id
        # 将卖家名称加入进去
        order_info["Seller"] = account

        # 选出AmazonOrderId和ASIN的最新的记录
        newest_record = "select * from amazon_orders as a where not exists" +\
                        "(select 1 from amazon_orders as b where b.AmazonOrderId=a.AmazonOrderId " +\
                        "and b.ASIN=a.ASIN and b.LastUpdateDate>a.LastUpdateDate)"
        sql = "select * from (%s) as t where t.AmazonOrderId='%s'" % (newest_record, order_info['AmazonOrderId'])
        cur.execute(sql)
        data = cur.fetchall()

        # 如果此次请求结果中的LastUpdateDate约数据库中的一样,说明已在数据库中记录,本次循环不用做任何处理
        if data and str(data[0][1]) == order_info['LastUpdateDate']:
            continue

        # 处理PaidDate
        if order_info['OrderStatus'] == 'Pending':
            order_info['PaidDate'] = "0000-00-00 00:00:00"
        else:
            # 如果数据库里有该订单的PaidDate,则用数据库中的PaidDate,否则用此次请求结果中的LastUpdateDate
            if data and (data[0][4] is not None):
                order_info['PaidDate'] = str(data[0][4])
            else:
                order_info['PaidDate'] = order_info['LastUpdateDate']

        # 如果数据库里有该订单的信息,说明不是新订单,不需要再去请求订单所包含的商品,否则需要。
        if data:
            for i in range(len(data)):
                order_info_cp = order_info.copy()
                order_info_cp['ASIN'] = data[i][2]
                order_info_cp['SellerSKU'] = data[i][3]
                order_info_cp['RequestId_2'] = data[i][41]
                try:
                    # 更新到数据库
                    mysqlconn.db_insert(conn, order_info_cp, 'amazon_orders')
                except pymysql.err.IntegrityError:
                    pass
        else:
            # 请求订单所包含的商品信息
            order_items = get_order_items(account, order_info['AmazonOrderId'])
            for i in range(len(order_items)):
                order_info_cp = order_info.copy()
                order_info_cp['ASIN'] = order_items[i]['ASIN']
                order_info_cp['SellerSKU'] = order_items[i]['SellerSKU']
                order_info_cp['RequestId_2'] = order_items[i]['RequestId_2']
                try:
                    # 更新到数据库
                    mysqlconn.db_insert(conn, order_info_cp, 'amazon_orders')
                except pymysql.err.IntegrityError:
                    pass
    conn.close()


if __name__ == "__main__":
    import datetime
    t = datetime.datetime.now() - datetime.timedelta(hours=3)
    t = datetime.datetime.strftime(t, "%Y-%m-%d %H:%M:%S")
    get_cr_orders(t)
    get_lu_orders(t)
