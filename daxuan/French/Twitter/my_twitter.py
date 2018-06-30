#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib
import time
import sys

from lxml import etree
from selenium import webdriver
from urllib import quote

reload(sys)
sys.setdefaultencoding( "utf-8" )

def scroll(keyword, tst):
    cap = webdriver.DesiredCapabilities.FIREFOX
    cap["phantomjs.page.settings.resourceTimeout"] = 1000
    cap["phantomjs.page.settings.loadImages"] = True
    cap["phantomjs.page.settings.disk-cache"] = True
    cap["phantomjs.page.settings.userAgent"] = "Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:50.0) Gecko/20100101 Firefox/50.0",
    cap["phantomjs.page.customHeaders.User-Agent"] = 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:50.0) Gecko/20100101 Firefox/50.0',

    kname = quote(keyword)
    url = "https://twitter.com/search?f=tweets&q={}&src=typd".format(kname)
    browser = webdriver.Firefox(desired_capabilities=cap)
    # browser = webdriver.PhantomJS(desired_capabilities=cap)
    browser.get(url)
    # start = int(time.time())
    time.sleep(30)
    timest = read_timest(browser)
    while timest > tst:
    # while 1:
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        timest = read_timest(browser)
        # end = int(time.time())
        # if end - start == scroll_time:
        #     break
    # html = browser.page_source
    # with open('twitter.html', 'w') as f:
    #     f.write(html)
    # browser.close()

def read_timest(browser):
    # f = open('twitter.html', 'rb')
    # html = f.read()
    # con = etree.HTML(html)
    """/li[last()]/div[@class="content"]/div[@class="stream-item-header"]/small/a/@data-original-title"""
    date = browser.find_element_by_xpath('//div[@class="stream"]/ol[@id="stream-items-id"]/li[last()]//div[@class="content"]//small/a/@title/text()')[0].decode('utf-8').split(" - ")[1]
    date = date.replace("年", '-').replace("月", '-').replace('日', '')
    Array = time.strptime(date, "%Y-%m-%d")
    timestamp = int(time.mktime(Array))
    print date
    return timestamp

if __name__ == '__main__':
    tst = 1528732800
    scroll("Emmanuel Macron", tst)
    # time.sleep(10)
    # timest = read_timest()
    # while timest > 1528286166:
    #     scroll_time += 10
    #     scroll("Emmanuel Macron", scroll_time)
    #     time.sleep(10)
    #     timest = read_timest()

