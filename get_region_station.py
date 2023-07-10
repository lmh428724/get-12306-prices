import requests
import re
from openpyxl import Workbook

# 可以在12306网站直接刷新 通过F12获取最新的站台版本信息 当前日期为2023年7月5日 获取的版本 station_version=1.9270
station_key_value_url = "https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9270"

# 获取所有城市的站台信息
def get_station_key_value():
    requests.packages.urllib3.disable_warnings()
    response = requests.get(station_key_value_url, verify=False)
    # 正则表达式
    pattern = r"@([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|\|\|"

    # 结果字典
    result = {}
    # @bjb | 北京北 | VAP | beijingbei | bjb | 0 | 0357 | 北京 | | |
    # 遍历所有匹配

    for match in re.finditer(pattern, response.text):
        # 获取第二个和第八个子字符串
        city = match.group(8)
        station = match.group(2)
        # 如果城市在字典中，就添加车站到列表中
        if city in result:
            result[city].append(station)
        # 否则，就创建一个新的列表
        else:
            result[city] = [station]
    return result


if __name__ == '__main__':
    title = ["区划", "车站信息"]
    wb = Workbook()
    ws = wb.active
    ws.append(title)
    infos = get_station_key_value()
    for city in infos:
        i = 0
        for station in infos[city]:
            line = ['', station]
            if (i == 0):
                line = [city, station]
            i = i + 1
            ws.append(line)
    wb.save("city-stations.xlsx")
