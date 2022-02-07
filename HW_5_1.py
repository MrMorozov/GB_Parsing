from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys as keys
import time
import pymongo
from pymongo import MongoClient
from pymongo import errors


# MAIL.RU - парсинг писем

# Логин тестового ящика: study.ai_172@mail.ru
# Пароль тестового ящика: NextPassword172#


url = 'https://mail.ru/'
login = 'study.ai_172@mail.ru'
passcode = 'NextPassword172#'
driver_path = '/home/mike/Study/GB/Parsing_1/Lesson_5/chromedriver'


chrome_options = Options()
chrome_options.add_argument("start-maximized")

driver = webdriver.Chrome(executable_path=driver_path, options=chrome_options)
driver.implicitly_wait(10)

driver.get(url)




# 1. Авторизация:
       
# Ввод логина и переход на страницу ввода пароля:
login_ = driver.find_elements(By.NAME,"login")
continue_ = driver.find_elements(By.XPATH,'//button[@class="button svelte-1da0ifw"]')
login_[0].send_keys(login)
continue_[0].click()

# Ввод пароля и переход на страницу почты:
password = driver.find_elements(By.NAME,"password")
password[0].send_keys(passcode)
continue_ = driver.find_elements(By.XPATH,'//button[@class="second-button svelte-1da0ifw"]')
continue_[0].click()

time.sleep(25)
    
# 2. Создать список всех писем
# 	2.1 Реализовать скрол
# 	Понять когда закончить скролл
# 	Добавить в список все письма избежав дубли, и не потеряв данные

grid =driver.find_element(By.XPATH,'//div[contains(@class,"styled scrollable_content")]') # элемент содержащий прокрутку и реагирующий на PgUp/PgDn

mails = []
last_mails = []
time.sleep(2)
i = 1
while True:
    cur_mails = driver.find_elements(By.XPATH,'//div[@class="ReactVirtualized__Grid__innerScrollContainer"]//a[contains(@class,"llc llc")]')
    cur_mail_refs = [ref.get_attribute('href') for ref in cur_mails]
    if cur_mail_refs == last_mails: break
    last_mails = cur_mail_refs
    for mail in cur_mail_refs:
        if mail not in mails:
            mails.append(mail)
    # mails = mails+cur_mails
    grid.send_keys(keys.PAGE_DOWN)
    time.sleep(1)
    print('Scrol',i)
    i += 1
    
# Проверка по количеству писем:

try:
    in_mails =   driver.find_element(By.XPATH,'//a[contains(@title,"Входящие")]')
    in_mails_ = int(in_mails.get_attribute('title').split(", ")[1].split(' ')[0])
    if len(mails) == in_mails_: print('Список писем составлен успешно!')
    else: print('Число писем должно быть', in_mails_, 'вместо', len(mails))
except Exception as e:
    print(e)
    
    
# 3. Проитерировать через все элементы списка
# 	Собрать необходимую инфу из каждого письма и поместить в базу 
# (от кого, дата отправки, тема письма, текст письма полный)

client = MongoClient('127.0.0.1', 27017) # Создали клиента
db = client['HW_5_1']   # Создали указатель на базу
col_name = "HW_5_1_Mail.ru"
collection = db[col_name] 

for ref in mails:
    print(ref)
    driver.get(ref)
    time.sleep(1)
    id_ = ref.split(':')[2]
    from_ = driver.find_element(By.XPATH,'//span[@class="letter-contact"]').get_attribute('title')
    date = driver.find_element(By.XPATH,'//div[@class="letter__date"]').text
    subject = driver.find_element(By.XPATH,'//h2[@class="thread-subject"]').text
    text = driver.find_element(By.XPATH,'//div[@class="letter-body__body-content"]').text
    
    data = {"_id":id_,     
                'From':from_,
                'Date':date,
                'Subject':subject,
                'Text':text}      
    try:
            collection.insert_one(data)
    except errors.DuplicateKeyError: pass


# Проверка по количеству документов:
print(collection.count() == len(mails))
# client.drop_database('HW_5_1')