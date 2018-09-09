# -*- coding: utf-8 -*-
"""
Created at: 18-4-23 上午7:47

@Author: Qian
"""

import time
import requests

from .config import *
from .my_time import *

# add the father dir into the path
import sys
sys.path.append('..')

from exceptions import *

__all__ = ['api_get', ]


def api_get(type_, *args, **kwargs):
    _function_dict = {
        'ListOrders': ListOrders,
        'ListOrderItems': ListOrderItems,
        'ListInventorySupply': ListInventorySupply,
        'RequestReport': RequestReport,
        'GetReportRequestList': GetReportRequestList,
        'GetReport': GetReport,
        'GetMyPriceForSKU': GetMyPriceForSKU,
    }
    if _function_dict.get(type_, None):
        _config = _function_dict.get(type_)(*args, **kwargs)
    else:
        raise APITypeError("No that type API yet")

    return get_page(_config)


# 根据config.py中的类实例发送请求,获取结果
def get_page(request_data):
    """根据ListOrders类的实例发送请求,获取结果
    循环请求三次,成功break, 三次失败报错
    page.status_code 不为200时, sleep一段时间
    """

    # flag用于请求错误计数
    flag = 0
    max_request_times = 3

    # 获取请求的方式, 目前只提供POST方法
    if request_data.request_method == 'POST':
        req = requests.post
    else:
        raise Exception("Wrong request_method")

    while flag < max_request_times:
        try:
            page = req(request_data.url, data=request_data.payload)
            if page.status_code == 200:
                return page
            flag += 1
            time.sleep(request_data.recovery_time)
        except:
            flag += 1
    raise RequestError("Have requested more than %i times" % flag)
