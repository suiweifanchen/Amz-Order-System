# -*- coding: utf-8 -*-
"""
Created at: 18-3-7 上午05:42

@Author: Qian
"""

from my_modules import mysqlconn

__all__ = ['SKU']

conn = mysqlconn.mysqlconn(db='amazon')
cur = conn.cursor()
cur.execute("select sku,Seller from sku where IsFBA='True';")
data = cur.fetchall()
conn.close()

SKU = {}
for i in data:
    if i[1] in SKU:
        SKU[i[1]].append(i[0])
    else:
        SKU[i[1]] = [i[0], ]

