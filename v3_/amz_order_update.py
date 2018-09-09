# -*- coding: utf-8 -*-
"""
Created at: 18-4-26 上午10:02

@Author: Qian
"""

import os
import datetime
from my_modules import mysqlconn

from BasicConfig.mysql_info import db_config
from BasicConfig.account_info import ACCOUNT_INFO
from handlers import update_orders, update_orderitems, update_inventory, update_myprice

import logging
from logging import config
dir_path = os.path.dirname(__file__)  # relative path, it wil get '' when run it in its dir
config.fileConfig(os.path.join(dir_path, 'BasicConfig/AmazonLogging.conf'))


def main(logger, Account, t=None):
    if not t:
        t = datetime.datetime.now() - datetime.timedelta(hours=3)
        t = t.strftime("%Y-%m-%d %H:%M:%S")

    conn = mysqlconn.mysqlconn(**db_config)

    # orders
    try:
        logger.info(Account['Seller'] + "\torders update start")
        # CreatedAfter
        conn.connect() if not conn.open else 1
        logger.info("CreatedAfter")
        r_oc = update_orders(conn, Account, CreatedAfter=t)
        # LastUpdatedAfter
        conn.connect() if not conn.open else 1
        logger.info("LastUpdatedAfter")
        r_ol = update_orders(conn, Account, LastUpdatedAfter=t)
    except:
        logger.exception(Account['Seller'] + "\torders update Error")
        r_oc = 0
        r_ol = 0

    # orderitems
    try:
        conn.connect() if not conn.open else 1
        logger.info(Account['Seller'] + "\torderitems update start")
        r_oi = update_orderitems(conn, Account)
    except:
        logger.exception(Account['Seller'] + "\torderitems update Error")
        r_oi = 0

    # price
    try:
        conn.connect() if not conn.open else 1
        logger.info(Account['Seller'] + "\tprice update start")
        r_p = update_myprice(conn, Account)
    except:
        logger.exception(Account['Seller'] + "\tprice update Error")
        r_p = 0

    # inventory
    try:
        conn.connect() if not conn.open else 1
        logger.info(Account['Seller'] + "\tinventory update start")
        r_i = update_inventory(conn, Account)
    except:
        logger.exception(Account['Seller'] + "\tinventory update Error")
        r_i = 0

    conn.close()
    return r_oc, r_ol, r_oi, r_i, r_p


if __name__ == '__main__':
    logger = logging.getLogger('main')
    logger.info("Update Orders, Inventory, Price")

    result = []
    for Seller in ACCOUNT_INFO:
        Account = ACCOUNT_INFO[Seller]
        logger.info(Account['Seller'] + "\tStart")
        result.append({Account['Seller']: main(logger, Account)})
    logger.debug(result)

    logger.info("All End")
