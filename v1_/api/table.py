# -*- coding: utf-8 -*-
"""
Created at: 18-1-11 下午5:31

@Author: Qian
"""

import os
import json
import datetime
import pandas as pd
from my_modules import mysqlconn


def get_orders_from_db(account, startdate=None, enddate=None, type="new and paid"):
    """从数据库中提取某段时间内的订单记录
    如果startdate未给定，默认是前一天00：00：00
    如果enddate未给定，默认None
    type可选,默认是"new and paid",值可以为"paid", "new and paid", "unpaid", "new but unpaid"

    使用示例：
    >>> d = get_orders_from_db("J", type="new but unpaid")
    >>> d
    """

    if not startdate:
        if account == "F":
            startdate = datetime.datetime.now() - datetime.timedelta(days=1)
            startdate = datetime.datetime.strftime(startdate, "%Y-%m-%d 00:00:00")
        else:
            startdate = datetime.datetime.now()
            startdate = datetime.datetime.strftime(startdate, "%Y-%m-%d %H:%M:%S")

    # 选出AmazonOrderId和ASIN的最新的记录
    newest_record = "select * from amazon_orders as a where not exists" +\
                    "(select 1 from amazon_orders as b where b.AmazonOrderId=a.AmazonOrderId " +\
                    "and b.ASIN=a.ASIN and b.LastUpdateDate>a.LastUpdateDate)"

    if enddate:
        sql = "select * from (%s) t where t.PaidDate>='%s' and t.LastUpdateDate<'%s'" % (newest_record, startdate, enddate)
    else:
        sql = "select * from (%s) as t where t.PaidDate>='%s'" % (newest_record, startdate)

    if type == "new and paid":
        # type为None，则返回 new and paid
        sql = sql + " and t.OrderStatus<>'Pending'"
    elif type == "paid":
        # 返回所有paid订单
        sql = "select * from (%s) as t where t.OrderStatus<>'Pending'" % newest_record
    elif type == "unpaid":
        # 返回所有unpaid订单
        sql = "select * from (%s) as t where t.OrderStatus='Pending'" % newest_record
    elif type == "new but unpaid":
        # 返回new and unpaid订单
        sql = "select * from (%s) as t where t.PurchaseDate>='%s'" % (newest_record, startdate)
        sql = sql + " and t.OrderStatus='Pending'"
    else:
        raise Exception("No such type")

    # 选出指定卖家的订单
    if account != "all":
        sql = sql + " and Seller='%s'" % account

    conn = mysqlconn.mysqlconn()
    cur = conn.cursor()
    cur.execute(sql)
    data = cur.fetchall()
    conn.close()
    return list(data)


def data_to_df(data):
    """将数据库中取出的数据转成pandas.DataFrame形式"""

    if isinstance(data, tuple):
        data = list(data)

    columns = ['AmazonOrderId', 'LastUpdateDate', 'ASIN',
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

    df = pd.DataFrame(data, columns=columns)
    df = df[['SalesChannel', 'PurchaseDate', 'PaidDate',
             'AmazonOrderId', 'SellerSKU', 'ASIN',
             'NumberOfItemsShipped', 'NumberOfItemsUnshipped', 'Amount',
             'CurrencyCode', 'ShipServiceLevel', 'EarliestShipDate',
             'LatestShipDate', 'EarliestDeliveryDate', 'LatestDeliveryDate',
             'Name', 'Phone', 'CountryCode',
             'StateOrRegion', 'City', 'AddressLine1',
             'AddressLine2', 'PostalCode', 'AddressType',
             'OrderType', 'IsReplacementOrder', 'LastUpdateDate',
             'OrderStatus', 'ShippedByAmazonTFM', 'IsBusinessOrder',
             'PaymentMethodDetail', 'BuyerName', 'IsPremiumOrder',
             'FulfillmentChannel', 'PaymentMethod', 'IsPrime',
             'ShipmentServiceLevelCategory']]
    return df


# 销售汇总
def sum_sales(account, startdate):

    conn = mysqlconn.mysqlconn()
    cur = conn.cursor()
    sql = "select distinct AmazonOrderId,Amount,CurrencyCode from amazon_orders " + \
          "where seller='%s' and PaidDate>'%s' and OrderStatus<>'Pending'"
    sql = sql % (account, startdate)
    cur.execute(sql)
    data = cur.fetchall()
    conn.close()

    file = os.path.join(os.path.dirname(__file__), "exchange_rate.json")
    with open(file, 'r') as f:
        exchange_rate = json.load(f)

    order_sum = 0
    amount_sum = 0
    if data:
        for i in data:
            # 判断是否为None
            if i[1]:
                code = i[2]
                order_sum += 1
                amount_sum += i[1] * exchange_rate[code]
        amount_sum = amount_sum / exchange_rate["USD"]

    result = "订单数量： " + str(order_sum) + "\n" + \
             "订单总金额(USD)： " + str(round(amount_sum, 2))

    return result


if __name__ == "__main__":
    r = sum_sales("F", "2018-01-01 00:00:00")
