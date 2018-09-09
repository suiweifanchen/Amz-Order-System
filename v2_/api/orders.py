# -*- coding: utf-8 -*-
"""
Created at: 18-1-30 上午8:41

@Author: Qian
"""

import re
import time
import pymysql
import datetime
import requests
from my_modules import mysqlconn
from xml.etree import ElementTree as et

from .SKU import SKU
from .my_time import *
from . import config as uc  # user_config 缩写
from .create_db import orders_fields, orderitems_fields, inventory_fields


# 根据config.py中的类实例发送请求,获取结果
def get_page(request_data):
    """根据ListOrders类的实例发送请求,获取结果
    循环请求三次,成功break, 三次失败报错
    page.status_code 不为200时, sleep一段时间
    """

    # flag用于请求错误计数
    flag = 0

    # 获取请求方式
    if request_data.request_method == 'POST':
        req = requests.post
    else:
        raise Exception("Wrong request_method")

    while True:
        try:
            page = req(request_data.url, data=request_data.payload)
            if page.status_code != 200:
                flag += 1
                if flag > 2:
                    flag -= 1
                    raise Exception
                else:
                    time.sleep(request_data.recovery_time)
                    continue
            else:
                return page
        except:
            flag += 1
            if flag > 2:
                raise Exception("RequestError %i times" % flag)
            else:
                pass


# 解析xml
def parse_to_dict(node, info_dict=None):
    """递归遍历node节点(ET解析xml的节点)下所有信息
    将{tag:text}键值对存入info_dict字典中
    使用示例：
    info_dict = parse_to_dict(root)
    info_dict形式如下：
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


# 字典扁平化
def flat_dict(orig_dict):
    """将多层字典扁平化，删除上层key
    即
    d = {'a': {'b': 1, 'c': 2}, 'd':3}
    d = flat_dict(d)
    d 将如下：
    {'b': 1, 'c': 2, 'd':3}
    """

    new_dict = {}
    for key in orig_dict:
        if isinstance(orig_dict[key], dict):
            # 递归
            new_dict.update(flat_dict(orig_dict[key]))
        else:
            new_dict[key] = orig_dict[key]
    return new_dict


# 格式化数据
def format_data(data, data_type):
    """格式化order_info里的数据：
    1. 将时间数据中的'T', 'Z'字符删除
    2. 将1970-01-01 00:00:00替换成0000-00-00 00:00:00
    3. 只取需要的信息
    """

    d = {}

    if data_type == 'order':
        keys = orders_fields
        # 时间字符串的正则表达式
        string = '^[-\d]{10}T[:\d]{8}Z$'
        for key in keys:
            if data.get(key):
                if re.search(string, data[key]):
                    data[key] = re.sub('[TZ]', ' ', data[key]).strip()
                if data[key] == "1970-01-01 00:00:00":
                    data[key] = "0000-00-00 00:00:00"
                d[key] = data[key]

    elif data_type == 'orderitem':
        keys = orderitems_fields
        if data.get('ItemPrice'):
            item_price = data.pop('ItemPrice')
            d['ItemPrice'] = item_price['Amount']
            d['CurrencyCode_IP'] = item_price['CurrencyCode']
        for key in keys:
            if data.get(key):
                d[key] = data[key]

    elif data_type == 'inventory':
        keys = inventory_fields
        for key in keys:
            if data.get(key):
                d[key] = data[key]

    else:
        raise Exception("DataType Error")

    return d


#################################################
# 通过ListOrders获取订单
def get_orders(rtype, account, t):
    """通过ListOrders获取order信息
    rtype 指要查询orders的类型,可以为'CreatedAfter' 或者 'LastUpdatedAfter'
    account 指要查询的账户
    t 指所要查询的时间, 格式 0000-00-00 00:00:00
    """

    # 对t做简单处理,以满足时区和格式的要求
    t = get_utc_time(t, tz='UTC')

    if rtype == 'CreatedAfter':
        order_list = _get_orders(account, created_after=t)
    elif rtype == 'LastUpdatedAfter':
        order_list = _get_orders(account, last_updated_date=t)
    else:
        raise Exception("ListOrders Type Error")
    return order_list


def _get_orders(account, created_after=None, last_updated_date=None):
    if created_after:
        lo = uc.ListOrders(account, CreatedAfter=created_after)
    elif last_updated_date:
        lo = uc.ListOrders(account, LastUpdatedAfter=last_updated_date)
    else:
        raise Exception("Not Setting The Time")

    orders = []

    page = get_page(lo)
    # 解析page（xml字符串）
    page = re.sub(re.compile(' xmlns="https.*?"'), '', page.text)
    root = et.fromstring(page)
    # next_token = root.find('ListOrdersResult').find('NextToken')
    request_id = root.find('ResponseMetadata').find('RequestId')
    order_nodes = root.find('ListOrdersResult').find('Orders').findall('Order')
    for node in order_nodes:
        order = parse_to_dict(node)
        order = flat_dict(order)
        order = format_data(order, 'order')
        order['RequestId'] = request_id.text
        # 将卖家名称加入进去
        order["Seller"] = account
        orders.append(order)
    return orders


# 处理得到的order_list,并加入数据库的amazon.orders表中
def handle_orders(order_list):
    """处理得到的订单
    如果在数据库中已经有该订单(相同AmazonOrderId),且LastUpdatedDate一样,则跳过
    如果在数据库中已经有该订单(相同AmazonOrderId),LastUpdatedDate不一样,则insert进数据库,并判断PaidDate
    如果在数据库中没有该订单,insert进数据库
    """

    conn = mysqlconn.mysqlconn(db='amazon')
    cur = conn.cursor()

    for order in order_list:
        # 选出该AmazonOrderId的最新的记录
        newest_record = "select * from orders as a where not exists" +\
                        "(select 1 from orders as b where b.AmazonOrderId=a.AmazonOrderId " +\
                        "and b.LastUpdateDate>a.LastUpdateDate)"
        sql = "select * from (%s) as t where t.AmazonOrderId='%s'" % (newest_record, order['AmazonOrderId'])
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
            if data and (data[0][4] is not None):
                order['PaidDate'] = str(data[0][4])
            else:
                order['PaidDate'] = order['LastUpdateDate']

        # insert进数据库
        try:
            mysqlconn.db_insert(conn, order, 'orders')
        except pymysql.err.IntegrityError:
            pass

    conn.close()
    return 1  # 1表示函数执行成功


#################################################
# 通过ListOrderItems获取订单所包含的具体商品信息
def get_order_items(account):
    """通过ListOrderItems获取订单所包含的具体商品信息
    挑出数据库中 在orders表中而不在orderitems表中 的AmazonOrderId
    通过ListOrderItems获取订单具体信息,加入orderitems表里
    """

    conn = mysqlconn.mysqlconn(db='amazon')
    cur = conn.cursor()

    # 挑出需要请求具体信息的AmazonOrderId
    date = datetime.datetime.now() - datetime.timedelta(weeks=1)
    cur.execute("select distinct AmazonOrderId from orders where Seller='%s' and LastUpdateDate>'%s'" % (account, date.strftime("%Y-%m-%d %H:%M:%S")))
    data = cur.fetchall()
    data_o = [i[0] for i in data]
    cur.execute("select distinct AmazonOrderId,ItemPrice from orderitems")
    data = cur.fetchall()
    data_oi = [i[0] for i in data]
    conn.close()
    id_list = [i for i in data_o if i not in data_oi] + [i[0] for i in data if i[1] is None and i[0] in data_o]

    item_list = []
    for i in id_list:
        item_list += _get_order_items(account, i)

    return item_list


def _get_order_items(account, order_id):
    item_list = []
    loi = uc.ListOrderItems(account, order_id)

    page = get_page(loi)
    # 解析page（xml字符串）
    page = re.sub(re.compile(' xmlns="https.*?"'), '', page.text)
    root = et.fromstring(page)
    # next_token = root.find('ListOrdersResult').find('NextToken')
    request_id = root.find('ResponseMetadata').find('RequestId')
    order_items = root.find('ListOrderItemsResult').find('OrderItems').findall('OrderItem')

    for node in order_items:
        order_item = parse_to_dict(node)
        # item_info = flat_dict(item_info)  # 此处不可用flat_dict(),因为有重复键
        order_item = format_data(order_item, 'orderitem')
        order_item['AmazonOrderId'] = order_id
        order_item['RequestId'] = request_id.text
        item_list.append(order_item)

    return item_list


# 将item_list中的数据加入数据库amazon.orderitems表中
def handle_order_items(item_list):
    """将item_list中的数据加入数据库"""

    conn = mysqlconn.mysqlconn(db='amazon')
    for item in item_list:
        # insert进数据库
        try:
            mysqlconn.db_insert(conn, item, 'orderitems')
        except pymysql.err.IntegrityError:
            mysqlconn.db_update(conn, item, ['AmazonOrderId', 'SellerSKU'], 'orderitems')
    conn.close()
    return 1


#################################################
# 获取指定账户的库存信息
def get_inventory(account, skus=None):
    """获取指定账户的库存信息
    account 指需要查询的账户
    skus 指要查询的产品的sku, 为list格式, 默认是SKU.py中的产品
    """

    if not skus:
        skus = SKU[account]

    inventory_list = []
    for i in skus:
        inventory_list += _get_inventory(account, i)

    return inventory_list


def _get_inventory(account, sku):
    inventory_list = []

    lis = uc.ListInventorySupply(account, sku)
    page = get_page(lis)
    # 解析page（xml字符串）
    page = re.sub(re.compile(' xmlns="http.*?"'), '', page.text)
    root = et.fromstring(page)

    # next_token = root.find('ListOrdersResult').find('NextToken')
    request_id = root.find('ResponseMetadata').find('RequestId')
    marketplace_id = root.find('ListInventorySupplyResult').find('MarketplaceId')
    members = root.find('ListInventorySupplyResult').find('InventorySupplyList').findall('member')
    for node in members:
        inventory = parse_to_dict(node)
        inventory = format_data(inventory, 'inventory')
        inventory['Seller'] = account
        inventory['MarketplaceId'] = marketplace_id.text
        inventory['RequestId'] = request_id.text
        inventory_list.append(inventory)

    return inventory_list


# 将inventory_list中的数据加入数据库amazon.inventory表中
def handle_inventory(inventory_list):
    """将inventory_list中的数据加入数据库"""

    conn = mysqlconn.mysqlconn(db='amazon')
    for inventory in inventory_list:
        if inventory.get('Condition'):
            # Condition 可能是mysql内部保留字, 所以加上 `` 符号insert和update才不会报错
            inventory['`Condition`'] = inventory.pop('Condition')

        try:
            mysqlconn.db_insert(conn, inventory, 'inventory')
        except pymysql.err.IntegrityError:
            mysqlconn.db_update(conn, inventory, ['SellerSKU', 'Seller'], 'inventory')

    conn.close()
    return 1


if __name__ == '__main__':
    pass
