# -*- coding: utf-8 -*-
# @Author : jinxinqiang
# @Time   : 2018/6/23 10:05

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from pyquery import PyQuery as pq
import logging
from config import *
import pymongo

client=pymongo.MongoClient(MONGON_URL)
db=client[MONGON_DB]



# logging.basicConfig(level=logging.DEBUG,
#                     format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

#chrome无头浏览器模式
# chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--headless')
# browser = webdriver.Chrome(chrome_options=chrome_options)

browser=webdriver.Chrome()
# browser.set_window_size(1400, 900)
# 隐式等待
# driver.implicitly_wait(10)

#显式等待
# 表示给browser浏览器一个10秒的加载时间
wait=WebDriverWait(browser, 10)

def search():
    print('正在搜索……')
    try:
        browser.get('https://www.taobao.com/')
        input = wait.until(EC.presence_of_element_located((By.ID, 'q')))
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_TSearchForm > div.search-button > button')))
        input.send_keys('美食')
        submit.click()
        #总页数100
        total=wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-pager > div > div > div > div.total')))
        get_products()
        return total.text
    except Exception :   #TimeoutException
        return search()

def next_page(page_number):
    print('正在翻页……')
    try:
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > input')))
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit')))
        input.clear()
        input.send_keys(page_number)
        submit.click()
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > ul > li.item.active > span'), str(page_number)))
        get_products()
    except Exception :
        next_page(page_number)

def get_products():
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-itemlist')))
    html=browser.page_source
    doc=pq(html)
    # 是查找id的标签  .是查找class 的标签  link 是查找link 标签 中间的空格表示里层
    lis = doc('#mainsrp-itemlist .items .item').items()
    for item in lis:
        product={
            'image':item.find('.pic.img'),
            'price': item.find('.price').text(),
            'deal': item.find('.deal-cnt').text(),
            'shop': item.find('.shop').text(),
            'location': item.find('.location').text(),
            'image': item.find('.pic .img').attr('src')
        }
        print(product)
        save_to_mongo(product)

def save_to_mongo(result):
    try:
        if db[MONGO_TABLE].insert(result):
            print('保存到MONGODB成功', result)
    except Exception:
        print('保存到MONGODB失败',result)


def main():
    try:
        total = search()
        total = int(re.compile(r'(\d+)').search(total).group(1))#正则提取页数
        for page_number in range(2,total + 1):
            next_page(page_number)
    except Exception:
        print('出错了')
    finally:
        browser.close()
        print('爬取完成！')


if __name__=='__main__':
    main()
