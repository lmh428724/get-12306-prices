import re
import requests
import json
import random
import time
import ast
from openpyxl import Workbook
from _datetime import datetime


# print(datetime.strptime("20230301",'%Y%m%d'))

# r = open('all_stations.txt', 'r')
# train_list1 = ast.literal_eval(r.readlines()[0])
# title = ["车次", "始发站", "终点站", "出发站", "到达站", "商务座 价格", "一等座 价格", "二等座/二等包座 价格", "高级软卧 价格",
#              "软卧/一等卧 价格", "硬卧/二等卧 价格", "软座 价格", "硬座 价格", "无座 价格"]
# wb = Workbook()
# ws = wb.active
# ws.append(title)
# x = open('station_key_value.txt', 'r',encoding='utf-8')
# train_list2 = ast.literal_eval(x.readlines()[0])
# for price in train_list2:
#     ws.append(price)
# print(train_list2)
# wb.save("train_v20230228.xlsx")


#
# url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9161'
# requests.packages.urllib3.disable_warnings()
# proxies = {
#     'https': 'https://127.0.0.1:11975',  # 查找到你的vpn在本机使用的https代理端口
#     'http': 'http://127.0.0.1:11975',  # 查找到vpn在本机使用的http代理端口
# }
# response = requests.get(url, verify=False )
# stations = re.findall(u'([\u4e00-\u9fa5]+)\|([A-Z]+)', response.text)
# stations = dict(stations)
# print(stations)  # 此处print出字典检查一下看看有没有问题
