import requests
from bs4 import BeautifulSoup
from pprint import pprint
import pandas as pd
import re

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


url = 'https://hh.ru/search/vacancy' 
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'}
name = 'Видео монтажер'


params = {'text':name,
            'area':1,
            'salary':'',
            'currency_code':'RUR',
            'experience':'doesNotMatter',
            'order_by':'relevance',
            'search_period':0,
            'items_on_page':50,
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
        data = {'Title':title,
                'Sal_min':pars_sal[0],
                'Sal_max':pars_sal[1],
                'Currency':pars_sal[2],
                'Description':description,
                'Employer':employer,
                'Location':location,
                'Link':link,
                'Resource':'hh.ru'}

        
        # print(data)
        
        # print("")
        df = df.append(data, ignore_index=True)
    if len(dom.find_all('a', {'class': 'bloko-button','data-qa':'pager-next'}))==0: # Выход из цикла
        break
    if page >=1000: break # Защита от зацикливания
    page += 1
df[['Title', 'Sal_min', 'Sal_max', 'Currency', 
    'Employer', 'Location','Description', 
    'Resource', 'Link']].to_csv(f'{name}.csv', index = None, float_format = '%.3f')

    # ЗАПИСАТЬ В ДФ 
    # сохранить в удобном формате
    # Закинуть на гит и выдать pul request.
    
    
    