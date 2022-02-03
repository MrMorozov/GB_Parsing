import pprint
from lxml import html
import requests
import datetime as dt
import pymongo
from pymongo import MongoClient
from pymongo import errors


url = 'https://yandex.ru/news/'
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'}




response = requests.get(url, headers=headers)

dom = html.fromstring(response.text)
items = dom.xpath('//*[@id="neo-page"]/div/div[2]/div/div[1]//section//div[contains(@class,"col_xs_")]')
news = []

client = MongoClient('127.0.0.1', 27017) # Создали клиента
db = client['HW_4_1']   # Создали укащатель на базу
col_name = "HW_4_1_Yandex"
collection = db[col_name] 


i = 1
for item in items:
    new = {}
    raw = item.xpath('.//h2/a/text()') # Не отфильтровыны элементы страницы объединияющие 4 новости
 
    if len(raw)==1: # мне проще отфильтровать здесь нежели в Xpath
        source = item.xpath('.//a[@class="mg-card__source-link"]/@aria-label')[0].split(": ")[1]
        title = raw[0].replace('\xa0', ' ')
        link = item.xpath('.//h2/a/@href')[0]
        pub_time = item.xpath('.//span[@class="mg-card-source__time"]/text()')
        
        # Можно отформатировать время, не успевал допилить, ошибки:
        # pub_dt = dt.datetime(dt.datetiеme.now().year,
        #             dt.datetime.now().month,
        #             dt.datetime.now().day,
        #             int(pub_time[0].split(":")[0]),
        #             int(pub_time[0].split(":")[1]))
        
        id_ = item.xpath('.//h2/a/@data-log-id')[0]
        data = {"_id":id_,     
                'Title':title,
                'DatTime':pub_time,
                'Link':link}

        
        try:
            collection.insert_one(data)
        except errors.DuplicateKeyError: pass
        print(i, title)
        i += 1
    

# pprint(fishing)
collection.count()

# Количество новостей соответствует данным на сайте (13 секций по 5), количество документов в коллекции тоже соответствует 65.

# client.drop_database('HW_4_1')