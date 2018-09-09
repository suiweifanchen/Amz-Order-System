# -*- coding: utf-8 -*-
"""
Created at: 18-5-9 上午7:00

@Author: Qian
"""

import os
import json
import datetime
from my_modules import mysqlconn
from jinja2 import Environment, FileSystemLoader

from BasicConfig.mysql_info import db_config
from BasicConfig.mail_config import send_mail, MAIL
from BasicConfig.account_info import ACCOUNT_INFO

import logging
from logging import config
dir_path = os.path.dirname(__file__)  # relative path, it wil get '' when run it in its dir
config.fileConfig(os.path.join(dir_path, 'BasicConfig/AmazonLogging.conf'))


def summary(seller, startdate):
    conn = mysqlconn.mysqlconn(**db_config)
    try:
        inventory_info = get_inventory(conn, seller)
        order_info = get_order_info(conn, seller, startdate)
        # 获取汇率信息
        file = os.path.join(os.path.dirname(__file__), "CurrencyRate/exchange_rate.json")
        with open(file, 'r') as f:
            exchange_rate = json.load(f)

        order_set = set()
        total_sales = 0
        total_items = 0
        for i in order_info:
            flag = 0  # the flag that the order has been handled
            if i[4]:
                order_set.add(i[0])
            total_items += i[4]
            total_sales += i[1] * exchange_rate[i[2]]
            for j in range(len(inventory_info)):
                if inventory_info[j]['SellerSKU'] == i[3]:
                    inventory_info[j]['QuantityOrdered'] += i[4]
                    flag = 1
            if not flag:
                inventory_info.append({'SellerSKU': i[3], 'QuantityOrdered': i[4], 'InStockSupplyQuantity': 0})

        total_sales = total_sales / exchange_rate['USD']
        total_sales = round(total_sales, 2)
        total_orders = len(order_set)
        orderitems = sorted(inventory_info, key=lambda x: x['QuantityOrdered'], reverse=True)
        return orderitems, total_sales, total_orders, total_items

    except: raise
    finally:
        conn.close()


def get_order_info(conn, seller, startdate):
    conn.connect() if not conn.open else 1
    sql = "select orders.AmazonOrderId,orders.Amount,orders.CurrencyCode,orderitems.SellerSKU,orderitems.QuantityOrdered,orders.LastUpdateDate " \
          "from orders left join orderitems on orders.AmazonOrderId=orderitems.AmazonOrderId " \
          "where orders.OrderStatus<>'Pending' and orders.PaidDate>='%s' and orders.Seller='%s' " \
          "order by orders.AmazonOrderId asc,orders.LastUpdateDate desc;"
    sql = sql % (startdate, seller)
    cur = conn.cursor()
    cur.execute(sql)
    data = cur.fetchall()
    cur.close()

    # delete the canceled order
    data = [i[:-1] for i in data if i[1] is not None]

    result = []
    # delete the duplicate data
    # Note: the latest record will be first, so it can get the latest record
    for i in data:
        if i not in result:
            result.append(i)

    return result


# get the inventory information
# now only select products in USA market
def get_inventory(conn, seller, MarketplaceId='ATVPDKIKX0DER'):
    conn.connect() if not conn.open else 1
    sql = "select SellerSKU,InStockSupplyQuantity from inventory where Seller='%s' and MarketplaceId='%s'" % (seller, MarketplaceId)
    cur = conn.cursor()
    cur.execute(sql)
    data = cur.fetchall()
    cur.close()

    result = [{'SellerSKU': i[0], 'QuantityOrdered': 0, 'InStockSupplyQuantity': i[1]} for i in data]
    return result


# 调用前面的函数获取数据,传入html模板中,返回html字符串
def get_html_string(account, date):
    """
    调用前面的函数获取数据,传入html模板中,返回html字符串
    :param account: 要查询的帐号
    :param date: 形式0000-00-00 00:00:00
    :return: html字符串
    """

    t = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S') - datetime.timedelta(days=1)
    startdate = datetime.datetime.strftime(t, '%Y-%m-%d %H:%M:%S')
    orderitems, total_sales, total_orders, total_items = summary(account, startdate)

    env = Environment(loader=FileSystemLoader(os.path.dirname(__file__), 'utf-8'))
    t = env.get_template("BasicConfig/mail_template.html")
    html = t.render(date=date[:10],
                    account=account,
                    orderitems=orderitems,
                    total_sales=total_sales,
                    total_orders=total_orders,
                    total_items=total_items)
    return html.replace('None', '0')


def main(account, date, to_who=None):
    try:
        html = get_html_string(account, date)
        subject = date[:10] + " Sales Summary (" + account + ")"
        if not to_who:
            to_who = account
        r = send_mail(to_who, subject, html=html)
    except Exception as e:
        return e
    else:
        return r


if __name__ == '__main__':
    logger = logging.getLogger('main')
    logger.info("sales_summary.py Start")
    logger_ss = logging.getLogger('main.SalesSummary')

    logger_ss.info("Running amz_order_update.py")
    path = os.path.join(os.path.dirname(__file__), 'amz_order_update.py')
    os.system("python3 " + path)

    date = datetime.datetime.now().strftime('%Y-%m-%d %H:00:00')
    # date = '2018-01-01 00:00:00'
    result = []
    for seller in ACCOUNT_INFO:
        logger_ss.info(seller + "\tSummary Start")
        result.append(main(seller, date))

    logger_ss.debug(result)
    logger.info("sales_summary.py End")
