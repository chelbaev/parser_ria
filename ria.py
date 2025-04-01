import time
import random as rd
import datetime

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium_stealth import stealth


def makeDriver():
    options = webdriver.ChromeOptions()
    options.add_argument('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36')
    options.add_argument("start-maximized")
    options.add_argument('--blink-settings=imagesEnabled=false')
    options.add_argument("--headless")  # Включение headless-режима
    options.add_argument("--disable-gpu")  # Отключение GPU (рекомендуется для headless)
    options.add_argument("--no-sandbox")  # Отключение sandbox (для Linux)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=options)
    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )

    return driver, options


def get_time(time_str):
    date_dict = {'янв': 1, 'фев': 2, 'мар': 3, 'апр': 4, 'мая': 5, 'июн': 6, 'июл': 7,
                     'авг': 8, 'сен': 9, 'окт': 10, 'ноя': 11, 'дек': 12}
    current_date = datetime.datetime.strptime(str(datetime.datetime.today()).split()[0], "%Y-%m-%d")
    time_str = time_str.split(',')
    date = current_date
    if len(time_str) == 1:
        date = str(current_date).split()[0] + " " + (time_str[0].split('.')[0])
        date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M")
    else:
        if time_str[0] == 'Вчера':
            date = date - datetime.timedelta(days=1)
            date = datetime.datetime(date.year, date.month, date.day, int(time_str[1].split(':')[0]), int(time_str[1].split(':')[1]))                
        else:
            date = datetime.datetime(current_date.year, date_dict[time_str[0].split()[1][:3]], 
                                    int(time_str[0].split()[0]), int(time_str[1].split(':')[0]), int(time_str[1].split(':')[1]))
    return date


def parse_ria (driver : webdriver.Chrome, second_driver : webdriver.Chrome):
    domain = 'https://ria.ru/'
    table = pd.DataFrame(columns=['time', 'name', 'link', 'descriptions', 'views', 'tags'])
    tmp_names = ['Политика', 'Наука', 'В мире', 'Экономика']
    driver.get(domain)
    elems = driver.find_elements(By.CLASS_NAME, 'cell-extension__item')
    links = list() 
    for elem in elems:
        if elem.text in tmp_names:
            links.append((elem.find_element(By.TAG_NAME, 'a').get_attribute('href'), elem.text))

    for link, topic in links:
        time.sleep(1 + rd.random()*(0.5))
        try:
            driver.get(link)
        except:
            print ("Cann't open " + link)
        elems = driver.find_elements(By.CLASS_NAME, 'list-item')      
        for elem in elems:
            info = elem.find_elements(By.CLASS_NAME, 'list-item__info-item')
            page_link = elem.find_element(By.CLASS_NAME, 'list-item__title')
            name = page_link.text
            if (len(info) != 2):
                array = ['-', name, page_link, '-', '-', '-', '-', link]
            else:
                views = info[1].text
                tmp_date = info[0].text
                date = get_time(tmp_date)
                page_link = page_link.get_attribute('href')
                second_driver.get(page_link)
                time.sleep(1 + rd.random()*(0.5))
                descriptions = second_driver.find_element(By.CLASS_NAME, 'article__body').find_elements(By.CLASS_NAME, 'article__text')
                descriptions = '\n    '.join([x.text for x in descriptions])
            array = [date, name, page_link, descriptions, views, [topic, 'ria_news']]
            table.loc[len(table)] = array
    second_driver.close()
    driver.close()
    return table

def parse ():
    driver, chrome_opt = makeDriver()
    second_driver = webdriver.Chrome(options=chrome_opt)
    result = parse_ria(driver, second_driver)
    result.to_csv('out.csv')

parse()