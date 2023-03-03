from selenium import webdriver
from datetime import date, timedelta
from datetime import datetime
import requests
import json
import re
import time
import ast
import random
from openpyxl import Workbook

station_key_value_url= "https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9161"
train_search_url = "https://search.12306.cn/search/v1/train/search?keyword={}&date={}"
query_by_train_no = "https://kyfw.12306.cn/otn/czxx/queryByTrainNo?train_no={}&from_station_telecode={}&to_station_telecode={}&depart_date={}"
query_ticket_price = "https://kyfw.12306.cn/otn/leftTicket/queryTicketPrice?train_no={}&from_station_no={}&to_station_no={}&seat_types={}&train_date={}"
# 列车的关键词GC-高铁/城际 D-动车 Z-直达 T-特快 K-快速 其他-1..8
train_key = ['G', 'C', 'D', 'Z', 'T', 'K', '1', '2', '4', '5', '6', '7', '8']
# 座位关键词
train_seat_type = {'G': '9MO', 'C': 'MOO', 'D': 'MOO', 'Z': '1341', 'T': '1341', 'K': '1341', '1': '1341', '2': '1341',
                   '4': '1341', '5': '1341', '6': '1341', '7': '1341', '8': '1341'}

def get_headers():
    # 这里是做了一个动态获取cookie
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    # 此处做了一个后台打开浏览器的设置
    browser = webdriver.Chrome(chrome_options=chrome_options)
    browser.get('https://www.12306.cn/index/index.html')
    # 这个等待3秒是为了防止网页还没加载完就下一步了，保证后续获取到cookie
    time.sleep(3)
    # 以下是获取cookie并组成完整的cookie
    Cookie = browser.get_cookies()
    strr = ''
    for c in Cookie:
        strr += c['name']
        strr += '='
        strr += c['value']
        strr += ';'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
        'Cookie': strr
    }
    # 检查是否成功获取cookie，也可以写一个循环来检查，我懒就没写了
    # print(headers)
    # 退出后台的浏览器，不退出会占内存的
    browser.quit()
    return headers

# 获取站台的key-value结构
def get_station_key_value():
    f = open('files/station_key_value.txt', 'w+',encoding='utf-8')
    requests.packages.urllib3.disable_warnings()
    response = requests.get(station_key_value_url, verify=False)
    stations = re.findall(u'([\u4e00-\u9fa5]+)\|([A-Z]+)', response.text)
    f.writelines(str(stations))
    f.flush()
    f.close()
    return


# 获取所有的车次
# 注意 在周五周六周日的车次数据和其他其他时间的数据会存在差异, 注意要全部查到
# 实例返回{'date': '20230217', 'from_station': '铜川东', 'station_train_code': 'C231', 'to_station': '西安', 'total_num': '6', 'train_no': '410000C23105'}
def train_search():
    headers = get_headers();
    f = open('files/all_train_list.txt', 'w+',encoding='utf-8')
    train_list_normal = []
    train_list_weekend = []
    # 选定一个除了周五周六周日的日期
    normal = date.today() + timedelta(days=8)
    # 选定一个周末的 数据
    weekend = date.today() + timedelta(days=10)
    # 所有的车次关键词
    print("车次数据爬取中...")
    print("获取到平时的车次数据:")
    for key in train_key:
        response = \
            json.loads(requests.get(train_search_url.format(key, normal.strftime('%Y%m%d')), headers=headers).text)[
                'data']
        time.sleep(random.uniform(0.9, 2.0))
        train_list_normal.extend(response)
        print(response)
    print("获取到高峰期的车次数据:")
    for key in train_key:
        response = \
            json.loads(requests.get(train_search_url.format(key, weekend.strftime('%Y%m%d')), headers=headers).text)[
                'data']
        time.sleep(random.uniform(0.9, 2.0))
        train_list_weekend.extend(response)
        print(response)
    train_list = []
    for item_x in train_list_normal:
        flag = True
        # 判断高峰期数组中有没有含有这个来自平时的车次
        for item_y in train_list_weekend:
            if (item_x['station_train_code'] == item_y['station_train_code']):
                flag = False
                break;
        # item_x 是高峰期里没有的车次
        if (flag):
            train_list.append(item_x)
            print("加了一个车次信息:" + item_x['station_train_code'])
    train_list.extend(train_list_weekend)
    # 对车次信息进行排序
    # 先根据车次头进行排序  re.search(r'(.?).*', x['station_train_code']).group(1) -> K1120 = K
    # 车次头相同再根据序号进行排序 int(re.search(r'.?(.*)', x['station_train_code']).group(1)) -> K1120 = 1120
    train_list.sort(key=lambda x: (re.search(r'(.?).*', x['station_train_code']).group(1),
                                   int(re.search(r'.?(.*)', x['station_train_code']).group(1))))

    print("车次数据爬取完毕!")
    print(train_list)
    f.writelines(str(train_list))
    f.flush()
    f.close()
    return


# 获取某车次的所有站点
def query_train_station():
    headers = get_headers();
    r = open('files/all_train_list.txt', 'r',encoding='utf-8')
    train_list = ast.literal_eval(r.readlines()[0])
    print("站点数据爬取中...")
    x = 0
    f = open('files/all_stations.txt', 'w+',encoding='utf-8')
    for item in train_list:
        try:
            train_no = item['train_no']
            fi = open('files/station_key_value.txt', 'r', encoding='utf-8')
            stations = dict(ast.literal_eval(fi.readlines()[0]))
            from_station = stations[item['from_station']]
            to_station = stations[item['to_station']]
            date = datetime.strptime(item['date'], '%Y%m%d').strftime("%Y-%m-%d")
            x = x + 1
            if (x / 1000 == 1.0):
                x = 0
                headers = get_headers();
                time.sleep(60)
            try:
                train_station_list = json.loads(
                    requests.get(
                        query_by_train_no.format(train_no, from_station, to_station, date),
                        headers=headers).text)[
                    'data']['data']
                time.sleep(random.uniform(0.9, 2.0))
            except:
                print("爬虫遭到反制,重置爬虫数据中...")
                time.sleep(6 * 60)
                headers = get_headers();
                train_station_list = json.loads(
                    requests.get(
                        query_by_train_no.format(train_no, from_station, to_station, date),
                        headers=headers).text)[
                    'data']['data']
            item['train_station_list'] = train_station_list
        except:
            continue
    print("站点数据爬取完毕!")
    f.writelines(str(train_list))
    f.flush()
    f.close()
    return


# 爬取车次的价格
def get_train_price(key):
    headers = get_headers();
    r = open('files/all_stations.txt', 'r',encoding='utf-8')
    train_list = ast.literal_eval(r.readlines()[0])
    x = 0
    key_train_price = []
    for item in train_list:
        if (key != re.search(r'(.?).*', item['station_train_code']).group(1)):
            continue
        train_no = item['train_no']
        total_num = len(item['train_station_list'])
        date = datetime.strptime(item['date'], '%Y%m%d').strftime("%Y-%m-%d")
        for i in range(0, total_num):
            for j in range(i + 1, total_num):
                try:
                    from_station_no = item['train_station_list'][i]['station_no']
                    to_station_no = item['train_station_list'][j]['station_no']
                    x = x + 1
                    if (x / 1000 == 1.0):
                        x = 0
                        headers = get_headers();
                        time.sleep(60)
                    try:
                        price_dict = get_price_http(date, from_station_no, headers, to_station_no, train_no,
                                                    train_seat_type[key])
                    except:
                        headers = deal_fanzhi()
                        price_dict = get_price_http(date, from_station_no, headers, to_station_no, train_no,
                                                    train_seat_type[key])
                    # D字头的列车会存在差异化的座位类型导致爬取的数据异常
                    if (key == 'D'):
                        try:
                            price_dict2 = get_price_http(date, from_station_no, headers, to_station_no, train_no, "IJO")
                        except:
                            headers = deal_fanzhi()
                            price_dict2 = get_price_http(date, from_station_no, headers, to_station_no, train_no, "IJO")
                        deal_special_price_list(price_dict, price_dict2)
                    price_list = transfer_price_list(price_dict)
                    row = [item['station_train_code'], item['from_station'], item['to_station'],
                           item['train_station_list'][i]['station_name'],
                           item['train_station_list'][j]['station_name'], price_list[0], price_list[1],
                           price_list[2],
                           price_list[3], price_list[4], price_list[-4], price_list[-3], price_list[-2],
                           price_list[-1]]
                    print(row)
                    key_train_price.append(row)
                except:
                    continue
    r = open('files/'+key + '_train_prices.txt', 'w+', encoding='utf-8')
    r.writelines(str(key_train_price))
    r.flush()
    r.close()
    return


def deal_special_price_list(price_dict, price_dict2):
    if price_dict2.__contains__('AI'):
        price_dict.__setitem__('A4', price_dict2['AI'])
        price_dict2.pop('AI')
    if price_dict2.__contains__('AJ'):
        price_dict.__setitem__('A3', price_dict2['AJ'])
        price_dict2.pop('AJ')
    for k, v in price_dict2.items():
        if not (price_dict.__contains__(k)):
            price_dict.__setitem__(k, v)


# 处理爬虫反制措施
def deal_fanzhi():
    print("爬虫遭到反制,重置爬虫数据中...")
    time.sleep(6 * 60)
    headers = get_headers();
    return headers


# 发送获取价格的请求
def get_price_http(date, from_station_no, headers, to_station_no, train_no, seat_type):
    price_dict2 = json.loads(requests.get(
        query_ticket_price.format(train_no, from_station_no, to_station_no, seat_type,
                                  date),
        headers=headers).text)['data']
    time.sleep(random.uniform(0.9, 2.0))
    return price_dict2


# 将获取的票价转化为数组
def transfer_price_list(price_list):
    tmp_info = {'A9': '', 'M': '', 'O': '', 'A6': '', 'A4': '', 'A3': '', 'A2': '', 'A1': '', 'WZ': ''}
    for k, v in price_list.items():
        if (tmp_info.__contains__(k)):
            tmp_info.__setitem__(k, v)
    result = []
    for item in tmp_info.values():
        result.append(item)
    return result


if __name__ == '__main__':
    # 准备excel表头
    title = ["车次", "始发站", "终点站", "出发站", "到达站", "商务座 价格", "一等座 价格", "二等座/二等包座 价格", "高级软卧 价格",
             "软卧/一等卧 价格", "硬卧/二等卧 价格", "软座 价格", "硬座 价格", "无座 价格"]
    wb = Workbook()
    ws = wb.active
    ws.append(title)
    # train_list = []
    # # 获取所有的车次
    # train_list = train_search()
    # # 获取站台的key-value结构
    # get_station_key_value()
    # # 获取车次的所有站点
    # query_train_station()
    for key in train_key:
        # 爬取价格存入文件
        get_train_price(key)
    for key in train_key:
        pricefile = open('files/'+key + '_train_prices.txt', 'r', encoding='utf-8')
        key_train_price = ast.literal_eval(pricefile.readlines()[0])
        for price in key_train_price:
            ws.append(price)
    wb.save("all_train_prices.xlsx")