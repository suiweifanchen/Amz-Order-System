# -*- coding: utf-8 -*-
"""
Created at: 18-1-24 下午2:26

@Author: Qian
"""

import requests

MAIL = {
    "test": {
        "to": [
            "abc@123.com",
        ],

        "cc": [
            "def@456.com",
        ],
    },
}


def send_mail(account, subject, text=None, html=None, files=None):
    mail_box = MAIL[account]
    data = {
        "from": "abc@123.com",
        "to": mail_box['to'],
        "cc": mail_box['cc'],
        "subject": subject,
        "text": text,
        "html": html,
    }

    if not text:
        data.pop("text")
    if not html:
        data.pop("html")
    if files:
        r = requests.post(
            "https://api.mailgun.net/XXXXXX",
            auth=("api", "key-123456789"),
            files=files,
            data=data
        )
    else:
        r = requests.post(
            "https://api.mailgun.net/XXXXXX",
            auth=("api", "key-123456789"),
            data=data
        )
    return r
