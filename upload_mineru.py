#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
**************************************************
*@File    :   upload_mineru.py
*@Time    :   2026/02/03 15:35:57
*@Author  :   小鸟鸣 
*@Version :   1.0
*@email    :  dengjingren@cn.wilmar-intl.com
**************************************************
'''

import requests
import os
from datetime import datetime



token = "eyJ0eXBlIjoiSldUIiwiYWxnIjoiSFM1MTIifQ.eyJqdGkiOiI1MjAwMDE5MyIsInJvbCI6IlJPTEVfUkVHSVNURVIiLCJpc3MiOiJPcGVuWExhYiIsImlhdCI6MTc2NjEyODEyOCwiY2xpZW50SWQiOiJsa3pkeDU3bnZ5MjJqa3BxOXgydyIsInBob25lIjoiIiwib3BlbklkIjpudWxsLCJ1dWlkIjoiYmY3YzhjMjItNGYzZS00MjZkLWE4ZWItNDgxZTBhN2RmZmY2IiwiZW1haWwiOiJkaW5nZGluZ2R1YW5nQG91dGxvb2suY29tIiwiZXhwIjoxNzY3MzM3NzI4fQ.MAIpW62US3f4E7dq9FHV91AgLBuqSF00dfdvUoNT7y09LaEJ1alfMSmJZd_uN69xFG7GeLZ5ad61OQxEHfJLJg"
url = "https://mineru.net/api/v4/file-urls/batch"
header = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}
# 这个 直接给 根目录
curdir = os.getcwd()
# 运行项目的时候   代码在子目录，就返回 子目录的 路径
curdir = os.path.dirname(__file__)
file_path = os.path.join(curdir, "人民日报下载")
pdf_path = os.path.join(file_path, f"人民日报-{datetime.now().strftime('%Y-%m-%d')}.pdf")

data = {
    "files": [
        {"name":"demo.pdf", "data_id": "abcd"}
    ],
    "model_version":"vlm"
}

try:
    response = requests.post(url,headers=header,json=data)
    if response.status_code == 200:
        result = response.json()
        print(f'response success. result: {result}')
        if result["code"] == 0:
            batch_id = result["data"]["batch_id"]
            urls = result["data"]["file_urls"]
            print('batch_id:{},urls:{}'.format(batch_id, urls))

            with open(pdf_path, 'rb') as f:
                for i, url in enumerate(urls):
                    res_upload = requests.put(url, data=f)
                    if res_upload.status_code == 200:
                        print(f"{url} upload success")
                    else:
                        print(f"{url} upload failed")
        else:
            print('apply upload url failed,reason:{}'.format(result.msg))
    else:
        print('response not success. status:{} ,result:{}'.format(response.status_code, response))
except Exception as err:
    print(err)