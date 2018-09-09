# -*- coding: utf-8 -*-
"""
Created at: 18-1-12 上午10:42

@Author: Qian
"""

import re
import datetime
import requests

__all__ = ['get_timestamp', 'get_utc_time']


def get_timestamp():
    # 从亚马逊的mws官方获取时间戳
    page = requests.get("https://mws.amazonservices.com/")
    string = '<Timestamp timestamp="(.*?)" />'
    pattern = re.compile(string)
    timestamp = re.findall(pattern, page.text)[0]
    timestamp = timestamp[:-5] + timestamp[-1]
    return timestamp


def get_utc_time(t=None, tz='UTC+8'):
    """返回与t对应的UTC时间
    t未给定,返回UTC当前时间
    tz指所在时区,形式如'UTC', 'UTC+8', 'UTC-8',默认'UTC+8'
    """

    string = '^20[-\d]{8} [:\d]{8}$'
    if not t:
        t = datetime.datetime.utcnow()
    elif re.search(string, t):
        if tz == 'UTC':
            t = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
        else:
            delta = tz.split('C')[1]
            if delta[0] == "+":
                delta = int(delta[1:])
                t = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                t = t - datetime.timedelta(hours=delta)
            elif delta[0] == "-":
                delta = int(delta[1:])
                t = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                t = t + datetime.timedelta(hours=delta)
            else:
                raise Exception("No such timezone")
    else:
        raise Exception("Time form should be like '0000-00-00 00:00:00'")

    return datetime.datetime.strftime(t, "%Y-%m-%dT%H:%M:%SZ")


if __name__ == "__main__":
    pass
