#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-04-25 20:00:14
# @Author  : guangqiang_xu (981886190@qq.com)
# @Version : $Id$

import requests
from selenium import webdriver
# from selenium.webdriver.common.by import By
import time
import urllib
import json
from lxml import etree
from readability.readability import Document
sess = requests.Session()
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append('../')
from crawl_xiciip import get_ip
from config import *
from log import spider_log


headers = {  
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',  
    'Accept-Encoding':'gzip, deflate',  
    'Accept-Language':'zh-CN,zh;q=0.9',  
    'Connection':'keep-alive',  
    'Host':'weixin.sogou.com',  
    'Upgrade-Insecure-Requests':'1',  
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',  
    }  
driver = webdriver.Firefox()

spider_name = 'weixin'
log_folder_name = '%s_logs' % spider_name
logger = spider_log(log_name=spider_name, log_folder_name=log_folder_name)

def login():
    try:
        driver.get('http://weixin.sogou.com/')
        driver.find_element_by_xpath('//a[@id="loginBtn"]').click()
        # driver.get_screenshot_as_file("wx_login.png")
        time.sleep(10)
        cookie_items = driver.get_cookies()
        cookie = {}
        for cookie_item in cookie_items:
            sess.cookies.set(cookie_item['name'], cookie_item['value'])
    except Exception as error:
        logger.error('登陆失败: {}'.format(error))

def get_content(keyword):

    # kname关键词，URL page 是页码，
    kname = urllib.quote(keyword)
    page = 1
    while 1:
        ip = get_ip.get_random_ip()
        url = 'http://weixin.sogou.com/weixin?query={}&type=2&page={}&ie=utf8'.format(kname, page)
        response = sess.get(url, proxies=ip, headers=headers)
        logger.info('requests url: {}, page: {}'.format(url, page))
        txt = response.text
        html = etree.HTML(txt)
        divs = html.xpath('//ul[@class="news-list"]/li/div[2]')
        if len(divs) <= 0:
            driver.close()
            break
        for url in [div.xpath('./h3/a/@data-share') for div in html.xpath('//ul[@class="news-list"]/li/div[2]')]:
            try:
                news_url = url[0]
                driver.get(news_url)
                logger.info('requests news url: {}'.format(news_url))
                time.sleep(2)
                txt = driver.page_source
                html = etree.HTML(txt)
                title = html.xpath('//h2/text()')[0].strip()
                # 发表时间
                try:
                    strdate = html.xpath('//div[@id="img-content"]/div[1]/em/text()')[0]
                except:
                    strdate = html.xpath('//span[@id="publish_time"]/text()')[0]
                # 公众号名字
                try:
                    public_name = html.xpath('//div[@id="img-content"]/div[1]/span/a/text()')[0].strip()
                except:
                    public_name = html.xpath('//strong[@class="profile_nickname"]/text()')[0].strip()

                content = ''.join(html.xpath('//div[@id="js_content"]//p//text()')).strip().replace('\n','').replace('\t','')

                item = {}
                item['keyword'] = keyword
                item['title'] = title
                item['date'] = strdate
                item['public_name'] = public_name
                item['content'] = content
                item['url'] = news_url

                with open('./wx_data.json','a+') as f:
                    f.write(json.dumps(item,ensure_ascii=False) + '\n')
            except:
                continue

        page += 1
        # # 最多101页
        # if page == 101:
        #     break

def wx_main():
    login()
    time.sleep(15)
    for keyword in search_list:
        get_content(keyword)
        driver.close()
        time.sleep(15)

if __name__ == '__main__':
    wx_main()
