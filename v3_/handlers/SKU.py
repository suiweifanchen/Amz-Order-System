# -*- coding: utf-8 -*-
"""
Created at: 18-4-28 上午10:52

@Author: Qian
"""

from my_modules import mysqlconn

# add the father dir into the path
import sys
sys.path.append('..')
from BasicConfig.mysql_info import db_config

__all__ = ['SKU']

conn = mysqlconn.mysqlconn(**db_config)
cur = conn.cursor()
cur.execute("select Seller,MarketplaceId,sku from sku;")
data = cur.fetchall()
conn.close()

SKU = {}
for i in data:
    if i[0] not in SKU:
        SKU[i[0]] = {}
    if i[1] not in SKU[i[0]]:
        SKU[i[0]][i[1]] = []
    SKU[i[0]][i[1]].append(i[2])