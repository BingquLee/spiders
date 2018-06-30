#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib
import time
import sys

from lxml import etree
from selenium import webdriver

reload(sys)
sys.setdefaultencoding( "utf-8" )

def scroll(url, roll_time):
    browser = webdriver.PhantomJS()
    browser.get(url)
    time.sleep(5)
    start = int(time.time())

    while 1:
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        end = int(time.time())
        browser.save_screenshot(str(end) + '.png')
        if end - start >= roll_time:
            break

    html = browser.page_source
    with open('facebook.html', 'wb') as f:
        f.write(html)

    browser.close()

def read_timest():
    f = open('facebook.html', 'rb')
    html = f.read()
    con = etree.HTML(html)
    date = con.xpath('//div[@class="_1xnd"][last()]/div[@class="_4-u2 _4-u8"][last()-1]//div[@class="l_c3pyo2v0u i_c3pynyi2f clearfix"]//div[@class="_5pcp _5lel _2jyu _232_"]//span[@class="fsm fwn fcg"]/a/abbr/@title')
    date = date[len(date)-1]
    print "date", date
    Array = time.strptime(date, "%Y-%m-%d %H:%M")
    timestamp = int(time.mktime(Array))
    return timestamp

if __name__ == '__main__':
    scroll_time = 30
    scroll("https://www.facebook.com/pg/MarineLePen/posts/", scroll_time)
    time.sleep(10)
    timest = int(read_timest())
    print timest
    while timest > 1526572800:
        scroll_time += 30
        scroll("https://www.facebook.com/pg/MarineLePen/posts/", scroll_time)
        time.sleep(10)
        timest = int(read_timest())
        print(timest)


