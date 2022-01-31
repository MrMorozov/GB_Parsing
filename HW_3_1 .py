import requests
from bs4 import BeautifulSoup
from pprint import pprint
import pandas as pd
import re
import pymongo
from pymongo import MongoClient
from pymongo import errors

def SalPar(strg):
    try:
        cur = strg.split(' ')[-1]
        parts = strg.split('–')
        start = strg.split(' ')[0]
        if len(parts) == 2:
            out = [float(re.sub("[^0-9]", "", parts[0])),
                   float(re.sub("[^0-9]", "", parts[1])), 
                   cur]
        elif len(parts) == 1:
            if start == 'от':
                out = [float(re.sub("[^0-9]", "", parts[0])),
                       None, 
                       cur]                  
            elif start == 'до':
                out = [None,
                       float(re.sub("[^0-9]", "", parts[0])), 
                       cur]
        else: out = [None,None,None]
    except: out = [None,None,None]
    return out
 
def my_print(vac):
    t = '\t'
    lf = '\n'
    str_ = ""
    for vac in selection:
        str_= 'ID:' + 3*t + str(vac["_id"]) + lf
        str_= str_ + 'Title:' + 2*t + str(vac[("_id")]) + lf
        str_= str_ + 'Sal min:' + 2*t + str(vac["Sal_min"]) +" " + str(vac["Currency"])+ lf
        str_= str_ + 'Sal max:' + 2*t + str(vac["Sal_max"]) +" " + str(vac["Currency"])+ lf
        str_= str_ + 'Employer:' + 1*t + vac["Employer"] + lf
        str_= str_ + 'Currency:' + 1*t + vac["Currency"] + lf     
        print(str_)


url = 'https://hh.ru/search/vacancy' 
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'}
name = 'Видео монтажер'

client = MongoClient('127.0.0.1', 27017) # Создали клиента
db = client['HW_3_1']   # Создали укащатель на базу
col_name = name.replace(" ", "_")
collection = db[col_name]   # Создали указатель на коллекцию соответствующей критерию поиска

params = {'text':name,
            'area':1,
            'salary':'',
            'currency_code':'RUR',
            'experience':'doesNotMatter',
            'order_by':'relevance',
            'search_period':0,
            'items_on_page':20,
            'no_magic':'true',
            'L_save_area':'true'}


continue_ = True
page = 0
vac_df = pd.DataFrame
# Таблица:
df = pd.DataFrame()
while continue_:
    params['page'] = page
    print('Page:',page+1)
    response = requests.get(url, params=params, headers = headers)
    dom = BeautifulSoup(response.text, 'html.parser')
    
    # Список объектов вакансий:
    vac_list = dom.find_all('div', {'class': 'vacancy-serp-item'})
    
    # Парсер:
    for vac in vac_list:
        vac_data = {}
        # Наименование вакансии:
        title = vac.find('a',{'data-qa':"vacancy-serp__vacancy-title"}).getText()
        link = vac.find('a',{'data-qa':"vacancy-serp__vacancy-title"}).get('href')

        # Заработная плата:
        try:    
            salary = vac.find('span',{'data-qa':"vacancy-serp__vacancy-compensation"}).getText()
            pars_sal = SalPar(salary)
        except:
            # salary = None 
            pars_sal = [None,None,None]
        # print(salary, pars_sal) 
          
        # Описание:
        try:    
            description = vac.find('div',{'class':"g-user-content"}).getText()
        except: 
            description = None       
        
         # Рзаботодатель:
        try:    
            employer = vac.find('a',{'data-qa':"vacancy-serp__vacancy-employer"}).getText()
        except: 
            employer = None         
            
         # Регион:
        try:    
            location = vac.find('div',{'data-qa':"vacancy-serp__vacancy-address"}).getText()
        except: 
            location = None
        # ID я решил брать с ID вакансии на сайте (может и не лучшая идея, для начала решил сделать так):
        id_ = int(link.split('?')[0].split('/')[-1]) # Если ошибка, пусть лучше скрипт падает чем не будет видно что, что-то не добавилось
        # Проверка уникальности можно было бы сделать и по ссылке, но что-то у меня сопротивлялось перед таким решением 
        # - слишком длинный идентификатор (что если база будет на несколько сотен миллионов записей?)
        data = {"_id":id_,     
                'Title':title,
                'Sal_min':pars_sal[0],
                'Sal_max':pars_sal[1],
                'Currency':pars_sal[2],
                'Description':description,
                'Employer':employer,
                'Location':location,
                'Link':link,
                'Resource':'hh.ru'}

        
        try:
            collection.insert_one(data)
        except errors.DuplicateKeyError: pass
    if len(dom.find_all('a', {'class': 'bloko-button','data-qa':'pager-next'}))==0: # Выход из цикла
        break
    if page >=1000: break # Защита от зацикливания
    page += 1
    

# Вторая часть задания:

import numpy as np    

collection.count() # 127 вместо 128 если не делать проверку на уникальность ID
currencyes = collection.distinct( "Currency" ) # Посмотрим какие есть валюты
salaries = collection.find

min_sal_rur = 50000 # Минимальная ЗП в рублях
min_sal_usd = min_sal_rur/77.61 # Минимальная ЗП в долларах США

selection = collection.find({"$or":[ 
    {
    "Sal_min" : { "$gte" : min_sal_rur},
    "Sal_max" : { "$gte" : min_sal_rur},
    "Currency" : { "$eq" : 'руб.'}
    }, 
    {
    "Sal_min" : { "$gte" : min_sal_usd},
    "Sal_max" : { "$gte" : min_sal_usd},
    "Currency" : { "$eq" : 'USD'}
    }
    ]})
# Печать результатот выборки:
for vac in selection:
    my_print(vac)





# client.drop_database('HW_3_1')

    