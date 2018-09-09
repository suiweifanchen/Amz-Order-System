# -*- coding: utf-8 -*-
"""
Created at: 18-2-2 上午6:38

@Author: Qian
"""

import os
import json
import logging
import datetime
from my_modules import mysqlconn
from jinja2 import Environment, FileSystemLoader

from api.SKU import SKU
from mail_config import send_mail

# 日志
logger = logging.getLogger("Amazon  sales_summary.py")
logger.setLevel(logging.DEBUG)
# 日志格式
fmt = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')
# 文件日志1, ERROR级别,用来每日跟踪程序状态,是否出错; 文件日志2, DEBUG级别,用来记录程序行为
# 文件日志1所在位置
today = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d")
log_dir = '/root/log/' + today
if not os.path.exists(log_dir):
    os.mkdir(log_dir)
# 文件日志1, ERROR级别
fh1 = logging.FileHandler(os.path.join(log_dir, 'amz_update_orders.log'))
fh1.setLevel(logging.ERROR)
fh1.setFormatter(fmt)
# 文件日志2
fh2 = logging.FileHandler(os.path.join(os.path.dirname(__file__), 'Amazon.log'))
fh2.setLevel(logging.DEBUG)
fh2.setFormatter(fmt)
# 将相应的handler添加在logger对象中
logger.addHandler(fh1)
logger.addHandler(fh2)


# 从orders表中提取订单数据,汇总出 总销售额,总订单数量
def get_summary_info(account, startdate):
    """从数据库中提取订单数据,汇总出 总销售额,总订单数量 和 订单号
    account 指要查询的帐号
    startdate 指要查询的开始时间
    函数返回total_sales, total_orders, order_list"""

    # 选出表orders中每个AmazonOrderId的最新的记录
    newest_record = "select * from orders as a where not exists" + \
                    "(select 1 from orders as b where b.AmazonOrderId=a.AmazonOrderId " + \
                    "and b.LastUpdateDate>a.LastUpdateDate)"
    # 选出 指定账户指定时间之后的非pending状态的 订单
    sql = "select t.AmazonOrderId,t.Amount,t.CurrencyCode from (%s) as t " \
          "where t.PaidDate>='%s' and t.OrderStatus<>'Pending'"
    sql = sql % (newest_record, startdate)
    sql = sql + " and t.Seller='" + account + "'"

    # 取数据
    conn = mysqlconn.mysqlconn(db='amazon')
    cur = conn.cursor()
    cur.execute(sql)
    data = cur.fetchall()
    conn.commit()
    # 删除没有Amount的订单（如果某个订单的amount为None,判断为被取消的订单）
    # data形式如[('001', 899, 'USD'), ('002', 49, 'CAD')]
    data = [i for i in data if i[1] is not None]
    total_sales, total_orders, order_list = _summary_info(data)

    return total_sales, total_orders, order_list


# 处理从orders表中取出的数据
def _summary_info(data):
    # 将订单号全部提取出来
    order_list = [i[0] for i in data]

    # 获取汇率信息
    file = os.path.join(os.path.dirname(__file__), "api/exchange_rate.json")
    with open(file, 'r') as f:
        exchange_rate = json.load(f)

    # 汇总出 总销售额,总订单数量
    total_orders = 0
    total_sales = 0
    for i in data:
        total_orders += 1
        total_sales += i[1] * exchange_rate[i[2]]
    total_sales = total_sales / exchange_rate['USD']
    total_sales = round(total_sales, 2)

    return  total_sales, total_orders, order_list


# 从orderitems和inventory表中取出商品信息
def get_item_info(account, order_list):
    """从orderitems和inventory表中取出商品信息
    account 指要查询的帐号
    order_list 指要从orderitems中查询的订单, 类型:list
    """

    # 取出order_list中订单号所涉及的产品的信息
    if order_list:
        sql = "select orderitems.SellerSKU,AmazonOrderId,QuantityOrdered,InStockSupplyQuantity" \
              " from orderitems left join inventory on orderitems.SellerSKU=inventory.SellerSKU"
        sql = sql + " where AmazonOrderId in %s;"
        sql = sql % str(tuple(order_list)).replace(",)", ")")
        # 取数据
        conn = mysqlconn.mysqlconn(db='amazon')
        cur = conn.cursor()
        cur.execute(sql)
        data = cur.fetchall()
        conn.close()
    else:
        data = ()
    skus, orderitems, total_items = _format_data(data)

    # 取出未涉及到的其他产品的库存信息
    sku_list = SKU[account]
    sku_list = [i for i in sku_list if i not in skus]
    sku_list = tuple(sku_list)
    sql = "select SellerSKU,null,null,InStockSupplyQuantity from inventory where SellerSKU in %s" % str(sku_list)
    conn = mysqlconn.mysqlconn(db='amazon')
    cur = conn.cursor()
    cur.execute(sql)
    data = cur.fetchall()
    conn.close()
    for i in data:
        orderitems.append({'SellerSKU': i[0], 'QuantityOrdered': i[2], 'InStockSupplyQuantity': i[3]})

    return orderitems, total_items


# 处理一下数据格式
def _format_data(data):
    d = {}
    skus = []
    total_items = 0
    for i in data:
        skus.append(i[0])
        total_items += i[2]
        if i[0] in d:
            d[i[0]][0] += i[2]
            d[i[0]][1] = i[3]
        else:
            d[i[0]] = [i[2], i[3]]
    orderitems = [{'SellerSKU': i,
                   'QuantityOrdered':d[i][0],
                   'InStockSupplyQuantity': d[i][1]}
                  for i in d]
    return skus, orderitems, total_items


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
    total_sales, total_orders, order_list = get_summary_info(account, startdate)
    orderitems, total_items = get_item_info(account, order_list)

    env = Environment(loader=FileSystemLoader(os.path.dirname(__file__), 'utf-8'))
    t = env.get_template("mail_template.html")
    html = t.render(date=date[:10],
                    account=account,
                    orderitems=orderitems,
                    total_sales=total_sales,
                    total_orders=total_orders,
                    total_items=total_items)
    return html.replace('None', '0')


def main(account, date):
    html = get_html_string(account, date)
    subject = date[:10] + " Sales Summary"
    r = send_mail(account, subject, html=html)
    return r


if __name__ == '__main__':
    logger.info("Start")
    # 更新数据库
    logger.info("Running amazon_db_update.py")
    path = os.path.join(os.path.dirname(__file__), 'amazon_db_update.py')
    os.system("python3 " + path)

    date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:00:00')
    # F
    logger.info("F")
    r_f = main('F', date)

    logger.info("All End")
