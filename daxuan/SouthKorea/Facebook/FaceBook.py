#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-04-02 10:32:37
# @Author  : guangqiang_xu (981886190@qq.com)
# @Link    : http://www.treenewbee.com/
# @Version : $Id$
import os
from selenium import webdriver
import time
import hashlib
from elasticsearch import Elasticsearch
import json
import sys
from lxml import etree



reload(sys)
sys.setdefaultencoding('utf-8')
from pymongo import MongoClient
from langconv import *

es = Elasticsearch()


def searchData(index, type, body):
    query_body = {"query": {"query_string": {"query": body}}}
    results = es.search(index=index, doc_type=type, body=query_body)
    date_list = results['hits']['hits']
    return date_list


def Traditional2Simplified(sentence):
    sentence = Converter('zh-hans').convert(sentence)
    return sentence

def scroll(url, roll_time):
    # browser = webdriver.PhantomJS(executable_path=r"F:\phantomjs-2.1.1-windows\bin\phantomjs.exe")
    # browser = webdriver.PhantomJS(service_args=['–ignore-ssl-errors=true', '–ssl-protocol=TLSv1'])
    browser = webdriver.Firefox()
    browser.get(url)
    time.sleep(5)
    start = int(time.time())

    while 1:
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        end = int(time.time())
        # browser.save_screenshot(str(end) + '.png')
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

def crawl_facebook(url, start_strdate, end_strdate):
    scroll_time = 300
    start_timeArray = time.strptime(start_strdate, "%Y-%m-%d")
    start_timest = int(time.mktime(start_timeArray))
    end_timeArray = time.strptime(end_strdate, "%Y-%m-%d")
    end_timest = int(time.mktime(end_timeArray))

    scroll(url, scroll_time)
    time.sleep(10)
    timestamp = read_timest()

    while timestamp > start_timest:
        scroll_time += 200
        scroll(url, scroll_time)
        time.sleep(10)
        timestamp = int(read_timest())

    f = open('facebook.html', 'rb')
    html = f.read()
    con = etree.HTML(html)
    divs = con.xpath('//div[@class="_4-u2 _4-u8"]')
    # try:
    #     id = con.xpath('//div[@id="u_0_f"]/a/text()')[0]
    # except:
    #     id = con.xpath('//div[@id="u_0_g"]/a/text()')[0]
    id = con.xpath('//div[@id="u_0_f"]/a/text()')[0]
    name = con.xpath('//h1[@id="seo_h1_tag"]/a/text()')[0]
    i = 1
    path = './face_html/'
    for div in divs:
        html = etree.tostring(div)
        if not os.path.exists(path):
            os.makedirs(path)
        with open(path + str(i) + '.html', 'w') as f:
            f.write(html)
        i += 1

    for x in range(1, i):
        item = {}
        f = open(path + str(x) + '.html', 'r')
        html = f.read()
        con = etree.HTML(html)
        txt = ''.join(con.xpath('//div[@class="text_exposed_root"]//p/text()'))
        if txt in "":
            continue
        hash_md5 = hashlib.md5(txt)
        Id = hash_md5.hexdigest()
        dian = ''.join(con.xpath('//div[@class="UFILikeSentenceText"]/span/text()'))
        comm = ''.join(con.xpath('//a[@class="UFIPagerLink"]/text()'))
        date = ''.join(con.xpath('//*[@class="timestampContent"]/text()'))
        print date
        # now_ts = time.time()
        # date = con.xpath(
        #     '//div[@class="_1xnd"][last()]/div[@class="_4-u2 _4-u8"][last()-1]//div[@class="l_c3pyo2v0u i_c3pynyi2f clearfix"]//div[@class="_5pcp _5lel _2jyu _232_"]//span[@class="fsm fwn fcg"]/a/abbr/@title')
        # date = date[len(date) - 1]
        # if '2017' not in date:
        #     date = '2018-' + date.replace("月", "-").replace("日", "").split(" ")[0]
        # else:
        #     date = date.replace("月", "-").replace("日", "")
        # Array = time.strptime(date, "%Y-%m-%d")
        # timestamp = int(time.mktime(Array))
        if '2017' not in date:
            date = ("2018-" + date.replace('月', '-').replace('日', '')).split(' ')[0]
        else:
            date = date.replace('年', '-').replace('月', '-').replace('日', '')
        try:
            Array = time.strptime(date, "%Y-%m-%d")
            timestamp = int(time.mktime(Array))
        except:
            continue
        print "date", date
        print "timestamp", timestamp
        if int(timestamp) < start_timest:
            break

        # 帖子赞数
        try:
            zan = int(re.search(r'\d+', dian.replace(',', '')).group())
        except:
            zan = 1

        if zan == "":
            zan = 0
        if timestamp >= start_timest and timestamp <= end_timest:
            stringDate = dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
            timesyear = time.localtime(timestamp).tm_year
            facebook_name = Traditional2Simplified(name)
            item['summary'] = ""
            item['keyword'] = facebook_name
            item['candidate'] = facebook_name
            item['source'] = "facebook"
            item['timestamp'] = int(timestamp)
            item['date'] = date
            item['cn'] = "cn"
            item['context'] = Traditional2Simplified(txt)
            item['timesyear'] = timesyear
            item['time'] = stringDate
            item['id'] = Id

            item['likes'] = zan
            item['comment'] = comm

            item['facebook_id'] = id

            with open('facebok.json', 'a') as f:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    wenzaiyin_url = "https://www.facebook.com/pg/moonbyun1/posts/"
    # hongzhunshao_url = "https://www.facebook.com/pg/joonpyohong21/posts/"
    anzhexiu_url = "https://www.facebook.com/pg/ahncs111/posts/"
    liuchengmin_url = "https://www.facebook.com/pg/yooseongmin21/posts/"
    shenxiangding_url = "https://www.facebook.com/pg/simsangjung/posts/"

    crawl_facebook(wenzaiyin_url, '2017-01-01', '2017-05-09')
    # crawl_facebook(hongzhunshao_url, '2017-01-01', '2017-05-09')
    crawl_facebook(anzhexiu_url, '2017-01-01', '2017-05-09')
    crawl_facebook(liuchengmin_url, '2017-01-01', '2017-05-09')
    crawl_facebook(shenxiangding_url, '2017-01-01', '2017-05-09')