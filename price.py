import re
import requests
from selenium import webdriver
import json
import time
from datetime import datetime


def getprice(string,headers):
    string = ''.join(string)

    # 提取票价关键信息
    # train_no: 560000G282C0 ->1
    # from_station_no 06 -> 15
    # to_station_no 08 -> 16
    # seat_types 9MO -> 33
    # train_date: 20230215 -> 12
    reg = re.compile(
        '.*?\|预订\|(.*?)\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|(.*?)\|.*?\|.*?\|(.*?)\|(.*?)\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|(.*?)\|.*')
    tran_info = list(re.findall(reg, string)[0])
    train_no = tran_info[0]
    from_station_no = tran_info[2]
    to_station_no = tran_info[-2]
    seat_types = tran_info[-1]
    train_date = datetime.strftime(datetime.strptime(tran_info[1], '%Y%m%d'), '%Y-%m-%d')

    queryTicketPriceUrl = 'https://kyfw.12306.cn/otn/leftTicket/queryTicketPrice?train_no={}&from_station_no={}&to_station_no={}&seat_types={}&train_date={}'.format(
        train_no, from_station_no, to_station_no, seat_types, train_date)
    response = json.loads(requests.get(queryTicketPriceUrl,headers=headers).text)
    tmp_info = {'A9': '', 'M': '', 'O': '', 'A6': '', 'A4': '', 'A3': '', 'A2': '', 'A1': '', 'WZ': ''}
    for k, v in response['data'].items():
        if (tmp_info.__contains__(k)):
            tmp_info.__setitem__(k, v)
    result = []
    for item in tmp_info.values():
        result.append(item)
    return result
