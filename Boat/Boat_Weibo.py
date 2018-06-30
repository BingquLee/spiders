#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-04-02 10:32:37
# @Author  : guangqiang_xu (981886190@qq.com)
# @Link    : http://www.treenewbee.com/
# @Version : $Id$
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import hashlib
import json
import sys
from lxml import etree

reload(sys)
sys.setdefaultencoding('utf-8')

class BoatWeibo(object):
    def __init__(self, email_addr, password):
        self.email_addr = email_addr
        self.password = password
        self.driver = webdriver.Firefox()

    def weibo_login(self):
        self.driver.get('https://weibo.com/')
        time.sleep(30)
        self.driver.find_element_by_xpath('//input[@id="loginname"]').clear()
        time.sleep(2)
        self.driver.find_element_by_xpath('//input[@id="loginname"]').send_keys('weiboxnr01@126.com')
        self.driver.find_element_by_xpath('//input[@type="password"]').clear()
        time.sleep(2)
        self.driver.find_element_by_xpath('//input[@type="password"]').send_keys('xnr123456')
        self.driver.find_element_by_xpath('//div[@class="info_list login_btn"]/a[@action-type="btn_submit"]').click()

    def crawl_boat(self, keyword):
        page = 1
        self.weibo_login()
        time.sleep(20)
        # self.driver.find_element_by_xpath('//div[@class=" gn_search_v2"]/input[@node-type="searchInput"]').send_keys(keyword)
        # self.driver.find_element_by_xpath('//div[@class=" gn_search_v2"]/input[@node-type="searchInput"]').send_keys(Keys.ENTER)
        # self.driver.find_element_by_xpath('div[@class="search_rese clearfix"]/a').click()
        try:
            while 1:
                url = r'https://s.weibo.com/weibo/{}&nodup=1&page={}'.format(keyword, page)
                # driver = webdriver.Firefox()
                self.driver.get(url)
                time.sleep(20)
                try:
                    self.driver.find_element_by_xpath('//div[@class="pl_noresult"]')  # 出现无搜索结果的div时跳出循环
                    break
                except:
                    pass
                item = {}
                news_urls_list = self.driver.find_elements_by_xpath('//div[@class="WB_cardwrap S_bg2 clearfix"]')  # 获取新闻列表
                if news_urls_list == []:
                    break
                for news in news_urls_list:
                    user_name =  news.find_element_by_xpath('.//a[@class="W_texta W_fb"]').get_attribute("nick-name")
                    print user_name
                    news_content = news.find_element_by_xpath('.//p[@class="comment_txt"]').text
                    print news_content
                    item["username"] = user_name
                    item["news_content"] = news_content
                    with open("news.json", 'a') as f:
                        f.write(json.dumps(item, ensure_ascii=False)+'\n')
                self.driver.find_element_by_xpath('//div[@class="W_pages"]/a').click()
                time.sleep(10)
                page += 1
        except BaseException, e:
            print e
            pass
        finally:
            self.driver.close()




if __name__ == '__main__':

    boat_weibo = BoatWeibo('weiboxnr01@126.com', 'xnr123456')
    # boat_weibo.crawl_boat("孙波航母".decode('utf-8'))
    # boat_weibo.crawl_boat("孙波军工".decode('utf-8'))
    # boat_weibo.crawl_boat("孙波落马".decode('utf-8'))
    # boat_weibo.crawl_boat("中船重工孙波被查".decode('utf-8'))
    boat_weibo.crawl_boat("中船重工孙波".decode('utf-8'))
    # boat_weibo.crawl_boat("孙波造船黑幕".decode('utf-8'))
