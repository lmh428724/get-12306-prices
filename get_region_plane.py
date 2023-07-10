import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook



# 解析网页，提取数据
def get_region_plane():
  # 网站的URL
  url = "https://flights.ctrip.com/booking/airport-guides.html"
  # 发送请求，获取网页内容
  response = requests.get(url)
  content = response.text
  soup = BeautifulSoup(content, "html.parser")
  items =soup.find("div", class_="airport_list").find_all("li")
  result = {}
  for item in items:
    # 提取城市名称和机场站名
    city = item.b.text.strip()
    station = item.a.text.strip()
    # 如果城市在字典中，就添加车站到列表中
    if city in result:
      result[city].append(station)
    # 否则，就创建一个新的列表
    else:
      result[city] = [station]
  return result
if __name__ == '__main__':
  title = ["城市名称", "机场名称"]
  wb = Workbook()
  ws = wb.active
  ws.append(title)
  infos = get_region_plane()
  for city in infos:
    i = 0
    for airplane in infos[city]:
      line = ['', airplane]
      if (i == 0):
        line = [city, airplane]
      i = i + 1
      ws.append(line)
  wb.save("city-airplane.xlsx")