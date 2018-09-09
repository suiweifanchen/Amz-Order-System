# -*- coding: utf-8 -*-
"""
Created at: 18-1-24 下午12:01

@Author: Qian
"""

import os
import time
import requests

code = ['USD', 'CAD', 'MXN']  # MXN墨西哥比索
exchange = {}

for i in code:
    url = "http://webforex.hermes.hexun.com/forex/quotelist?code=FOREX%sCNY&column=code,price,PriceWeight,UpdownRate&callback=ongetjsonpforex&_=1516767097894"
    url = url % i
    page = requests.get(url)
    price = page.text.split(',')[1]
    PriceWeight = page.text.split(',')[2]
    exchange[i] = float(price) / float(PriceWeight)
    time.sleep(1)

file = os.path.join(os.path.dirname(__file__), "exchange_rate.json")
with open(file, 'w') as f:
    f.writelines(str(exchange).replace("'", '"'))

pass
