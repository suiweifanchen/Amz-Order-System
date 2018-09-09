# -*- coding: utf-8 -*-
"""
Created at: 18-5-10 上午4:44

@Author: Qian
"""

from my_modules import mysqlconn

from BasicConfig.mysql_info import db_config
from BasicConfig.account_info import ACCOUNT_INFO
from BasicConfig.create_db import amazon_db_sql, orders_table_sql, orderitems_table_sql, inventory_table_sql, sku_table_sql, price_table_sql
from handlers import update_orders, update_orderitems


def create_db():
    conn = mysqlconn.mysqlconn(**db_config)
    try:
        cur = conn.cursor()
        for sql in [amazon_db_sql, orders_table_sql, orderitems_table_sql, inventory_table_sql, sku_table_sql, price_table_sql]:
            cur.execute(sql)
        cur.close()
    except: raise
    finally:
        conn.close()


# get order information from amazon and store into db
def flush_info_to_db(Account, t):

    conn = mysqlconn.mysqlconn(**db_config)

    # orders
    try:
        # CreatedAfter
        conn.connect() if not conn.open else 1
        r_oc = update_orders(conn, Account, CreatedAfter=t)
        # LastUpdatedAfter
        conn.connect() if not conn.open else 1
        r_ol = update_orders(conn, Account, LastUpdatedAfter=t)
    except:
        r_oc = 0
        r_ol = 0

    # orderitems
    try:
        conn.connect() if not conn.open else 1
        r_oi = update_orderitems(conn, Account)
    except:
        r_oi = 0

    conn.close()
    return r_oc, r_ol, r_oi


if __name__ == '__main__':
    create_db()

    account = {
        'Test': ['2018-06-01 00:00:00', ],
    }

    result = []
    for seller in account:
        for date in account[seller]:
            result.append(flush_info_to_db(ACCOUNT_INFO[seller], date))

    print(result)

