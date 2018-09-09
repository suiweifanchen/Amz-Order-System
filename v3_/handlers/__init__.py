# -*- coding: utf-8 -*-
"""
Created at: 18-4-24 上午10:34

@Author: Qian
"""

import re
import time
import datetime
from pandas import DataFrame
from my_modules import mysqlconn
from xml.etree import ElementTree as ET

from .SKU import SKU

# add the father dir into the path
import sys
sys.path.append('..')

from rules import *
from api import api_get
from BasicConfig.create_db import sku_fields

amazon_time_format = '^[-\d]{10}T[:\d\.]+?Z$'
human_time_format = '^[-\d]{10} [:\d]{8}$'


#################################################
# parse the xml object
def xml_parser(node, rules):
    if not rules:
        return 0

    xml_info = dict()

    for i in rules['Common_Info']:
        if node.findall(rules[i]):
            xml_info[i] = node.findall(rules[i])[0].text

    xml_info['Results'] = []
    results = node.findall(rules['results'])[0]
    result_list = results.findall(rules['result_list'])
    for child_node in result_list:
        temp = dict()
        for i in rules.keys():
            if (i not in rules['Not_In']) and child_node.findall(rules[i]):  # maybe it has not that info
                temp[i] = child_node.findall(rules[i])[0].text

        xml_info['Results'].append(temp)
        del temp

    return xml_info


def is_FBA(conn, SellerId, MarketplaceId, SellerSKU):
    sql = "select FulfillmentChannel from price where SellerId='%s' and MarketplaceId='%s' and SellerSKU='%s'" % (SellerId, MarketplaceId, SellerSKU)
    cur = conn.cursor()
    cur.execute(sql)
    data = cur.fetchall()
    cur.close()

    if data and data[0][0] == "AMAZON":
        return True
    else:
        return False


#################################################
# ListOrders
def get_orders(Account, CreatedAfter=None, LastUpdatedAfter=None):
    # transfer datetime format
    if CreatedAfter and re.search(human_time_format, CreatedAfter):
        CreatedAfter = CreatedAfter.replace(' ', 'T') + 'Z'
    if LastUpdatedAfter and re.search(human_time_format, LastUpdatedAfter):
        LastUpdatedAfter = LastUpdatedAfter.replace(' ', 'T') + 'Z'

    response = api_get('ListOrders', Account=Account, CreatedAfter=CreatedAfter, LastUpdatedAfter=LastUpdatedAfter)
    root = ET.fromstring(re.sub(re.compile(' xmlns="http.*?"'), '', response.text))
    _result = xml_parser(root, LIST_ORDERS)

    # transfer the datetime in _result
    result = []
    for i in _result['Results']:
        i['RequestId'] = _result['RequestId']
        i['Seller'] = Account['Seller']
        for key in i:
            if re.search(amazon_time_format, i[key]):
                i[key] = i[key].replace('T', ' ').replace('Z', '')
            if i[key] == "1970-01-01 00:00:00":
                i[key] = "0000-00-00 00:00:00"
        result.append(i)

    return result


# -------------------------------------------------
def update_orders(conn, Account, CreatedAfter=None, LastUpdatedAfter=None):
    order_list = get_orders(Account=Account, CreatedAfter=CreatedAfter, LastUpdatedAfter=LastUpdatedAfter)

    cur = conn.cursor()

    # 处理得到的订单
    # 如果在数据库中已经有该订单(相同AmazonOrderId), 且LastUpdatedDate一样, 则跳过
    # 如果在数据库中已经有该订单(相同AmazonOrderId), LastUpdatedDate不一样, 则insert进数据库, 并判断PaidDate
    # 如果在数据库中没有该订单, insert进数据库
    for order in order_list:
        # 选出该AmazonOrderId的最新的记录
        newest_record = "select * from orders as a where not exists" + \
                        "(select 1 from orders as b where b.AmazonOrderId=a.AmazonOrderId " + \
                        "and b.LastUpdateDate>a.LastUpdateDate)"
        sql = "select AmazonOrderId,LastUpdateDate,PaidDate from (%s) as t where t.AmazonOrderId='%s'" % (newest_record, order['AmazonOrderId'])
        cur.execute(sql)
        data = cur.fetchall()

        # 如果此次请求结果中的LastUpdateDate约数据库中的一样,说明已在数据库中记录，不用做任何处理
        if data and str(data[0][1]) == order['LastUpdateDate']:
            continue

        # 处理PaidDate
        if order['OrderStatus'] == 'Pending':
            order['PaidDate'] = "0000-00-00 00:00:00"
        else:
            # 如果数据库里有该订单的PaidDate,则用数据库中的PaidDate,否则用此次请求结果中的LastUpdateDate
            if data and (data[0][2] is not None):
                order['PaidDate'] = str(data[0][2])
            else:
                order['PaidDate'] = order['LastUpdateDate']

        # insert进数据库
        try:
            mysqlconn.db_insert(conn, order, 'orders')
        except mysqlconn.pymysql.err.IntegrityError:
            pass

    cur.close()
    return 1  # 1表示函数执行成功


#################################################
# ListOrderItems
def get_orderitems(Account, AmazonOrderId):
    response = api_get('ListOrderItems', Account=Account, AmazonOrderId=AmazonOrderId)
    root = ET.fromstring(re.sub(re.compile(' xmlns="http.*?"'), '', response.text))
    _result = xml_parser(root, LIST_ORDER_ITEMS)

    result = []
    for i in _result['Results']:
        i['RequestId'] = _result['RequestId']
        i['AmazonOrderId'] = _result['AmazonOrderId']
        result.append(i)

    return result


# -------------------------------------------------
def update_orderitems(conn, Account, orderid_list=tuple()):
    if not orderid_list:
        # 挑出需要请求具体信息的AmazonOrderId
        date = datetime.datetime.now() - datetime.timedelta(weeks=4)
        cur = conn.cursor()
        cur.execute("select distinct AmazonOrderId from orders where Seller='%s' and LastUpdateDate>'%s'" % (Account['Seller'], date.strftime("%Y-%m-%d %H:%M:%S")))
        data = cur.fetchall()
        data_o = [i[0] for i in data]
        cur.execute("select distinct AmazonOrderId,ItemPrice_Amount from orderitems")
        data = cur.fetchall()
        data_oi = [i[0] for i in data]
        cur.close()
        orderid_list = tuple([i for i in data_o if i not in data_oi] + [i[0] for i in data if i[1] is None and i[0] in data_o])

    for id in orderid_list:
        orderitem_list = get_orderitems(Account=Account, AmazonOrderId=id)

        for item in orderitem_list:
            # insert进数据库
            try:
                mysqlconn.db_insert(conn, item, 'orderitems')
            except mysqlconn.pymysql.err.IntegrityError:
                mysqlconn.db_update(conn, item, ['AmazonOrderId', 'SellerSKU'], 'orderitems')

    return 1


#################################################
# ListInventorySupply
def get_inventory(Account, MarketplaceId, SKU):
    response = api_get('ListInventorySupply', Account=Account, MarketplaceId=MarketplaceId, SKU=SKU)
    root = ET.fromstring(re.sub(re.compile(' xmlns="http.*?"'), '', response.text))
    _result = xml_parser(root, LIST_INVENTORY_SUPPLY)

    result = []
    for i in _result['Results']:
        i['Seller'] = Account['Seller']
        i['RequestId'] = _result['RequestId']
        i['MarketplaceId'] = _result['MarketplaceId']
        result.append(i)

    return result


# -------------------------------------------------
def update_inventory(conn, Account, market_list=tuple(), sku_list=dict()):
    if not market_list:
        market_list = tuple([Account[key] for key in Account if key.startswith('MarketplaceId')])
    if not sku_list and SKU.get(Account['Seller']):
        sku_list = SKU[Account['Seller']]

    for MarketplaceId in market_list:
        if not sku_list.get(MarketplaceId):
            continue
        for sku in sku_list.get(MarketplaceId):
            inventory_list = get_inventory(Account=Account, MarketplaceId=MarketplaceId, SKU=sku)

            for inventory in inventory_list:
                if inventory.get('Condition'):
                    # Condition 可能是mysql内部保留字, 所以加上 `` 符号insert和update才不会报错
                    inventory['`Condition`'] = inventory.pop('Condition')

                try:
                    mysqlconn.db_insert(conn, inventory, 'inventory')
                except mysqlconn.pymysql.err.IntegrityError:
                    if is_FBA(conn, Account['SellerId'], MarketplaceId, sku):
                        mysqlconn.db_update(conn, inventory, ['SellerSKU', 'Seller', 'MarketplaceId'], 'inventory')

    return 1


#################################################
# GetMyPriceForSKU
def get_myprice(Account, MarketplaceId, SKU):
    response = api_get('GetMyPriceForSKU', Account=Account, MarketplaceId=MarketplaceId, SKU=SKU)
    root = ET.fromstring(re.sub(re.compile(' xmlns="http.*?"'), '', response.text))
    _result = xml_parser(root, GET_MY_PRICE_FOR_SKU)

    result = []
    for i in _result['Results']:
        i['Seller'] = Account['Seller']
        i['RequestId'] = _result['RequestId']
        result.append(i)

    return result


# -------------------------------------------------
def update_myprice(conn, Account, market_list=tuple(), sku_list=dict()):
    if not market_list:
        market_list = tuple([Account[key] for key in Account if key.startswith('MarketplaceId')])
    if not sku_list and SKU.get(Account['Seller']):
        sku_list = SKU[Account['Seller']]

    for MarketplaceId in market_list:
        if not sku_list.get(MarketplaceId):
            continue
        for sku in sku_list.get(MarketplaceId):
            myprice_list = get_myprice(Account=Account, MarketplaceId=MarketplaceId, SKU=sku)

            for myprice in myprice_list:
                # insert进数据库
                try:
                    mysqlconn.db_insert(conn, myprice, 'price')
                except mysqlconn.pymysql.err.IntegrityError:
                    mysqlconn.db_update(conn, myprice, ['SellerSKU', 'SellerId', 'MarketplaceId'], 'price')

    return 1


#################################################
# Reports
# SKU
def get_mysku(Account, MarketplaceId, ReportType):
    ReportRequestId = request_report(Account=Account, MarketplaceId=MarketplaceId, ReportType=ReportType)
    ReportId = get_report_request_list(Account=Account, ReportRequestId=ReportRequestId)
    report = get_report(Account=Account, ReportId=ReportId)
    data = report_parse(report)
    return data, ReportId


def update_mysku(conn, Account, MarketplaceId, ReportType):
    data, ReportId = get_mysku(Account=Account, MarketplaceId=MarketplaceId, ReportType=ReportType)

    # filter the data using pandas.DataFrame
    df = DataFrame(data[1:], columns=data[0])
    columns = [i for i in sku_fields if i in data[0]]
    df = df[columns]
    df['Seller'] = Account['Seller']
    df['MarketplaceId'] = MarketplaceId
    df['ReportId'] = ReportId

    result = []
    # delete the old sku
    cur = conn.cursor()
    cur.execute('delete from sku where MarketplaceId="%s" and Seller="%s";' % (MarketplaceId, Account['Seller']))
    conn.commit()
    cur.close()
    # update sku to db
    for i in range(df.shape[0]):
        dct = {}
        for j in df.columns:
            dct[j] = df[j][i] if df[j][i] != '' else 'NULL'
        try:
            mysqlconn.db_insert(conn, dct, 'sku')
        except Exception as e:
            result.append(e)
            pass

    return result


def request_report(Account, MarketplaceId, ReportType):
    response = api_get('RequestReport', Account=Account, MarketplaceId=MarketplaceId, ReportType=ReportType)
    root = ET.fromstring(re.sub(re.compile(' xmlns="http.*?"'), '', response.text))
    _result = xml_parser(root, REQUEST_REPORT)

    result = []
    for i in _result['Results']:
        i['RequestId'] = _result['RequestId']
        result.append(i)

    return result[0]['ReportRequestId']


def get_report_request_list(Account, ReportRequestId):
    flag = 20
    while flag:
        response = api_get('GetReportRequestList', Account=Account, ReportRequestId=ReportRequestId)
        root = ET.fromstring(re.sub(re.compile(' xmlns="http.*?"'), '', response.text))
        _result = xml_parser(root, GET_REPORT_REQUEST_LIST)

        result = []
        for i in _result['Results']:
            i['RequestId'] = _result['RequestId']
            result.append(i)

        if result[0]['ReportProcessingStatus'] == "_DONE_":
            return result[0]['GeneratedReportId']
        else:
            del response, root, _result, result
            flag -= 1
            time.sleep(30)
            continue

    raise TimeoutError("Wait More Than 10 minutes")


def get_report(Account, ReportId):
    response = api_get('GetReport', Account=Account, ReportId=ReportId)
    return response.text


def report_parse(page_string):
    data = page_string.split('\r\n')
    for i in range(len(data)):
        if i == 0:
            data[i] = data[i].replace(' ', '')
        data[i] = data[i].split('\t')
    return data[:-1]


if __name__ == '__main__':
    pass
