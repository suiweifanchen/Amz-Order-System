# -*- coding: utf-8 -*-
"""
Created at: 18-1-24 下午2:24

@Author: Qian
"""

import datetime
import requests
from api.table import sum_sales
from mail_config import MAIL as mail_box

t = datetime.datetime.now() - datetime.timedelta(days=1)
t = datetime.datetime.strftime(t, "%Y-%m-%d %H:%M:00")
now = datetime.datetime.now() + datetime.timedelta(hours=8)
now = datetime.datetime.strftime(now, "%Y-%m-%d")
text = sum_sales("F", t)
mail_box = mail_box["F"]

r = requests.post(
    "https://api.mailgun.net/XXXXXX",
    auth=("api", "key-123456789"),
    data={"from": "abc@123.com",
          "to": mail_box['to'],
          "cc": mail_box['cc'],
          "subject": now + "   Sales Summary",
          "text": "F\nDaily Sales Summary\n" + "\n" + text,
          }
)
