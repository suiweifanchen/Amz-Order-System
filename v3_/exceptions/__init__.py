# -*- coding: utf-8 -*-
"""
Created at: 18-4-28 上午7:03

@Author: Qian
"""


class APITypeError(Exception):
    """API Calling Error: It may occur when you call a api function that is not in the list"""


class ArgsError(Exception):
    """Args Using Error: It may occur when you miss or mistake some args on calling a function"""


class RequestError(Exception):
    """API Request Error: It may occur when your net is not well or your request is too frequently"""


class DatetimeError(Exception):
    """Datetime Format Error: It may occurs when you give a datetime sting in wrong format"""
