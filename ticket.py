# # from stations import stations
# from prettytable import PrettyTable
# from selenium import webdriver
# import datetime
# from price import getprice
# import requests
# import json
# import re
# import time
# from openpyxl import Workbook
#
# def get_headers():
#     # 这里是做了一个动态获取cookie
#     chrome_options = webdriver.ChromeOptions()
#     chrome_options.add_argument('--headless')
#     # 此处做了一个后台打开浏览器的设置
#     browser = webdriver.Chrome(chrome_options=chrome_options)
#     browser.get('https://www.12306.cn/index/index.html')
#     # 这个等待3秒是为了防止网页还没加载完就下一步了，保证后续获取到cookie
#     time.sleep(3)
#     # 以下是获取cookie并组成完整的cookie
#     Cookie = browser.get_cookies()
#     strr = ''
#     for c in Cookie:
#         strr += c['name']
#         strr += '='
#         strr += c['value']
#         strr += ';'
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
#         'Cookie': strr
#     }
#     # 检查是否成功获取cookie，也可以写一个循环来检查，我懒就没写了
#     # print(headers)
#     # 退出后台的浏览器，不退出会占内存的
#     browser.quit()
#     return headers
#
#
# def get_tickets(froms, tos, date, headers):
#     # 转换名称为简称
#     froms = stations[froms]
#     tos = stations[tos]
#
#     # 构建链接
#     request_url = 'https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT'.format(
#         date, froms, tos)
#     # 发送请求
#     response = json.loads(requests.get(request_url, headers=headers).text)
#     # 获取结果
#     result = response['data']['result']
#     new_list = []
#     for item in result:
#         if not '列车停运' in item:
#             new_list.append(item)
#         else:
#             pass
#     return new_list
#
# # 获取用户输入的信息
# def get_info():
#     # fw = input("请输入出发地>>>")
#     # tw = input("请输入目的地>>>")
#     fw = "南京南"
#     tw = "徐州东"
#     st = input("请输入出发时间；格式：(年-月-日)(默认为今日日期)>>>>")
#     if st == '':
#         st = datetime.date.today()
#         return fw, tw, st
#     else:
#         today = datetime.date.today()
#         date = str(today).split('-')
#         list = st.split('-')
#         if int(list[0]) < int(date[0]) or int(list[0]) > int(date[0]):
#             exit("输入的年份不在我的查询范围之内")
#         else:
#             if int(list[1]) < int(date[1]) or int(list[1]) > int(date[1]) + 1:
#                 exit("你输入的月份不在我的查询范围之内")
#             else:
#                 if int(list[2]) < int(date[2]):
#                     exit("你输入的日期不在我的查询范围之内")
#                 else:
#                     if int(list[1]) < 10 and int(list[1][0]) != 0:
#                         list[1] = '0' + list[1]
#                     if int(list[2]) < 10 and int(list[2][0]) != 0:
#                         list[2] = '0' + list[2]
#                     return fw, tw, list[0] + '-' + list[1] + '-' + list[2]
#
#
# # 解析车次信息
# def decrypt1(string):
#     string = ''.join(string)
#     reg = re.compile(
#         '.*?\|预订\|.*?\|(.*?)\|.*?\|.*?\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|.*?\|.*?\|.*?\|.*')
#     result = list(re.findall(reg, string)[0])
#     result[1] = new_dict[result[1]]
#     result[2] = new_dict[result[2]]
#     results = [result[0], result[1], result[2], result[3], result[4], result[5], result[-1], result[-2], result[-3],
#                result[-12], result[-10], result[-6], result[-5], result[-8], result[-4], result[-7]]
#     return results
#
#
# # title = ["车次", "出发站", "到达站", "出发时间", "到达时间", "历时", "商务座", "价格", "一等座", "价格", "二等座", "价格", "高级软卧", "价格", "软卧", "价格",
# #          "动卧", "价格", "硬卧", "价格", "软座", "价格", "硬座", "价格", "无座", "价格"]
# # headers = {};
#
# if __name__ == '__main__':
#     title = ["车次", "出发站", "到达站", "出发时间", "到达时间", "历时", "商务座", "商务座价格", "一等座", "一等座价格", "二等座", "二等座价格", "高级软卧", "高级软卧价格", "软卧", "软卧价格",
#          "动卧", "动卧价格", "硬卧", "硬卧价格", "软座", "软座价格", "硬座", "硬座价格", "无座", "无座价格"]
#     # pt = PrettyTable()
#     # pt.title='车次表'
#     # pt.field_names = title
#     headers = get_headers()
#     [fw, tw, st] = get_info()
#     trainlist = get_tickets(fw, tw, st, headers)
#     new_dict = {v: k for k, v in stations.items()}
#     wb = Workbook()
#     ws = wb.active
#     ws.append(title)
#     for item in trainlist:
#         ticketInfo = decrypt1(item);
#         priceInfo = getprice(item, headers);
#         row = [ticketInfo[0], ticketInfo[1], ticketInfo[2], ticketInfo[3], ticketInfo[4], ticketInfo[5], ticketInfo[6],
#                priceInfo[0], ticketInfo[7], priceInfo[1], ticketInfo[8], priceInfo[2], ticketInfo[9], priceInfo[3],
#                ticketInfo[10], priceInfo[4], ticketInfo[11], "--", ticketInfo[12], priceInfo[5],
#                ticketInfo[13], priceInfo[6], ticketInfo[14], priceInfo[7], ticketInfo[15], priceInfo[8]]
#         # pt.add_row(row)
#         ws.append(row)
#     # print(pt)
#     wb.save("sample.xlsx")