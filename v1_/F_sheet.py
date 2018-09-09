# -*- coding: utf-8 -*-
"""
Created at: 18-1-12 下午12:32

@Author: Qian
"""

import os
import requests
import datetime

from api.table import get_orders_from_db
from api.table import data_to_df


def send_message(files, account):
    """发送邮件"""
    mailboxes = ["abc@123.com", ]
    results = []
    for i in mailboxes:
        r = requests.post(
            "https://api.mailgun.net/XXXXXX",
            auth=("api", "key-123456789"),
            files=files,
            data={"from": "abc@123.com",
                  "to": i,
                  "subject": "Daily Sales Sheet",
                  "text": "这是 %s 的Daily Sales Sheet, 请查收~" % account}
        )
        results.append(r)
    return results


file_path = os.path.dirname(__file__) + "/sheets_folder/" + datetime.datetime.now().strftime('%Y%m%d')
if not os.path.exists(file_path):
    os.mkdir(file_path)


def get_sales_sheet(account):
    files = []
    base_name = file_path + "/" + account

    # new and paid
    orders_data = get_orders_from_db(account, type="new and paid")
    df = data_to_df(orders_data)
    file_name = base_name + "_new and paid.csv"
    df.to_csv(file_name)
    files.append(("attachment", (file_name.split("/")[-1], open(file_name, "rb").read())))
    
    # # paid
    # orders_data = get_orders_from_db(account, type="paid")
    # df = data_to_df(orders_data)
    # file_name = base_name + "_paid.csv"
    # df.to_csv(file_name)
    # # files.append(("attachment", (file_name.split("/")[-1], open(file_name, "rb").read())))

    # # unpaid
    # orders_data = get_orders_from_db(account, type="unpaid")
    # df = data_to_df(orders_data)
    # file_name = base_name + "_unpaid.csv"
    # df.to_csv(file_name)
    # # files.append(("attachment", (file_name.split("/")[-1], open(file_name, "rb").read())))

    # new but unpaid
    orders_data = get_orders_from_db(account, type="new but unpaid")
    df = data_to_df(orders_data)
    file_name = base_name + "_new but unpaid.csv"
    df.to_csv(file_name)
    files.append(("attachment", (file_name.split("/")[-1], open(file_name, "rb").read())))

    return files


f = get_sales_sheet("F")
r = send_message(f, "F")
