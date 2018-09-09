# -*- coding: utf-8 -*-
"""
Created at: 18-4-23 上午7:49

@Author: Qian
"""

import re
import requests

__all__ = ['get_timestamp', ]


def get_timestamp():
    # 从亚马逊的mws官方获取时间戳
    page = requests.get("https://mws.amazonservices.com/")
    string = '<Timestamp timestamp="(.*?)" />'
    pattern = re.compile(string)
    timestamp = re.findall(pattern, page.text)[0]
    timestamp = timestamp[:-5] + timestamp[-1]
    return timestamp


if __name__ == "__main__":
    pass
