# -*- coding: utf-8 -*-
"""
Created at: 18-3-5 上午6:58

@Author: Qian
"""

import re
import time
import pymysql
import pandas as pd
from my_modules import mysqlconn

from .orders import get_page
from .create_db import sku_fields
from .config import GetReport, GetReportRequestList, RequestReport


def up_products(account):
    result = []
    report = get_product_report(account, '_GET_FLAT_FILE_OPEN_LISTINGS_DATA_')

    conn = mysqlconn.mysqlconn(db='amazon')
    for i in range(report.shape[0]):
        dct = {}
        for j in report.columns:
            dct[j] = report[j][i] if report[j][i] != '' else 'NULL'
        try:
            mysqlconn.db_insert(conn, dct, 'sku')
        except pymysql.err.IntegrityError:
            mysqlconn.db_update(conn, dct, ['sku', 'Seller'], 'sku')
        except Exception as e:
            result.append(e)
            pass
    conn.close()

    return result


def get_product_report(account, report_type):
    report_request_id = request_report(account, report_type)
    report_id = get_report_request_list(account, report_request_id)
    # report_id = '8599794632017595'
    page = get_report(account, report_id)
    data = handle_data(page.text)
    df = pd.DataFrame(data[1:], columns=data[0])
    columns = [i for i in sku_fields if i in data[0]]
    df = df[columns]
    df['Seller'] = account
    df['IsFBA'] = ['True' if df['quantity'][i] == '' else 'False' for i in range(df.shape[0])]
    return df


def request_report(account, report_type):
    rr = RequestReport(account, report_type)
    page = get_page(rr)

    string = "<ReportRequestId>(.*?)</ReportRequestId>"
    pattern = re.compile(string)
    report_request_id = re.findall(pattern, page.text)[0]

    return report_request_id


def get_report_request_list(account, report_request_id):
    flag = 20
    while flag:
        grrl = GetReportRequestList(account, report_request_id)
        page = get_page(grrl)

        string = "<ReportProcessingStatus>(.*?)</ReportProcessingStatus>"
        pattern = re.compile(string)
        status = re.findall(pattern, page.text)[0]
        if status == "_DONE_":
            string = "<GeneratedReportId>(.*?)</GeneratedReportId>"
            pattern = re.compile(string)
            report_id = re.findall(pattern, page.text)[0]
            return report_id
        else:
            flag -= 1
            time.sleep(30)
            continue
    raise Exception("Wait More Than 10 minutes")


def get_report(account, report_id):
    gr = GetReport(account, report_id)
    page = get_page(gr)
    return page


def handle_data(page_string):
    data = page_string.split('\r\n')
    for i in range(len(data)):
        if i == 0:
            data[i] = data[i].replace(' ', '')
        data[i] = data[i].split('\t')
    return data[:-1]


if __name__ == '__main__':
    pass
