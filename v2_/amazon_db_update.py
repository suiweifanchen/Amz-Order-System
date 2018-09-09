# -*- coding: utf-8 -*-
"""
Created at: 18-2-2 上午3:46

@Author: Qian
"""

import os
import logging
import datetime

from api.orders import get_orders, handle_orders
from api.orders import get_order_items, handle_order_items
from api.orders import get_inventory, handle_inventory

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


def main(account, t=None):
    if not t:
        t = datetime.datetime.now() - datetime.timedelta(hours=2)
        t = datetime.datetime.strftime(t, "%Y-%m-%d %H:%M:%S")

    # orders
    try:
        logger.info(account + "   orders start")
        # CreatedAfter
        logger.info("CreatedAfter")
        oc = get_orders('CreatedAfter', account, t)
        r_oc = handle_orders(oc)
        # LastUpdatedAfter
        logger.info("LastUpdatedAfter")
        ol = get_orders('LastUpdatedAfter', account, t)
        r_ol = handle_orders(ol)
    except:
        logger.exception(account + "   orders Error")
        r_oc = 0
        r_ol = 0

    # orderitems
    try:
        logger.info(account + "   orderitems start")
        oi = get_order_items(account)
        r_oi = handle_order_items(oi)
    except:
        logger.exception(account + "   orderitems Error")
        r_oi = 0

    # inventory
    try:
        logger.info(account + "   inventory start")
        i = get_inventory(account)
        r_i = handle_inventory(i)
    except:
        logger.exception(account + "   inventory Error")
        r_i = 0

    return r_oc, r_ol, r_oi, r_i



if __name__ == '__main__':
    logger.info("Update Orders and Inventory")
    # F
    logger.info("F Start")
    result_f = main('F')

    logger.info("All End")
