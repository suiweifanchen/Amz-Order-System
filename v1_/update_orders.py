# -*- coding: utf-8 -*-
"""
Created at: 18-1-12 上午11:25

@Author: Qian
"""

import os
import logging
import datetime

from api.orders import get_cr_orders
from api.orders import get_lu_orders
from api.create_db_tables import create_orders_table

# 日志
logger = logging.getLogger("Amazon update_orders.py")
logger.setLevel(logging.ERROR)
# 日志格式
fmt = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')
# 日志文件所在位置
today = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d")
log_dir = '/root/log/' + today
if not os.path.exists(log_dir):
    os.mkdir(log_dir)
# 文件日志, DEBUG级别
fh = logging.FileHandler(os.path.join(log_dir, 'amz_update_orders.log'))
fh.setLevel(logging.ERROR)
fh.setFormatter(fmt)
# 将相应的handler添加在logger对象中
logger.addHandler(fh)

try:
    create_orders_table()
    t = datetime.datetime.now() - datetime.timedelta(hours=3)
    t = datetime.datetime.strftime(t, "%Y-%m-%d %H:%M:%S")
    get_cr_orders("F", t, 'UTC')
    get_lu_orders("F", t, 'UTC')
except:
    logger.exception("error")

