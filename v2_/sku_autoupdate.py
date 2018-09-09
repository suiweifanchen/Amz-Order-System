# -*- coding: utf-8 -*-
"""
Created at: 18-4-2 上午4:36

@Author: Qian
"""

import os
import pymysql
import logging
import datetime
from my_modules import mysqlconn

from api.products import up_products

#################################################
# 日志
logger = logging.getLogger("Amazon  amazon_db_update.py")
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


#################################################
# 将sku表中非FBA产品的库存同步到inventory表中
def sku_to_inventory():
    sql = "select sku,Seller,quantity,asin from sku where IsFBA<>'True';"

    try:
        conn = mysqlconn.mysqlconn(db='amazon')
        cur = conn.cursor()
        cur.execute(sql)
        data = cur.fetchall()
        for i in data:
            try:
                mysqlconn.db_insert(
                    conn,
                    {'SellerSKU': i[0], 'Seller': i[1], 'InStockSupplyQuantity': i[2], 'ASIN': i[3], },
                    'inventory'
                )
            except pymysql.err.IntegrityError:
                mysqlconn.db_update(
                    conn,
                    {'SellerSKU': i[0], 'Seller': i[1], 'InStockSupplyQuantity': i[2], 'ASIN': i[3], },
                    ['SellerSKU', 'Seller'],
                    'inventory'
                )
    finally:
        conn.close()


# up_products
logger.info("Update Products(Sales Available)")
logger.info("F")
result_f = up_products('F')
if result_j or result_f:
    logger.error(str(result_j + result_jx + result_f))

logger.info("sku_to_inventory")
sku_to_inventory()
logger.info("Update Products End")
