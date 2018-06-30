#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-14 10:23:04
# @Author  : guangqiang_xu (981886190@qq.com)
# @Link    : http://www.treenewbee.com/
# @Version : $Id$

import os
import requests
from lxml import etree
from selenium import webdriver
from elasticsearch import Elasticsearch
from urllib import quote
import datetime
import time
import hashlib
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

es = Elasticsearch()

cap = webdriver.DesiredCapabilities.PHANTOMJS
cap["phantomjs.page.settings.resourceTimeout"] = 1000
cap["phantomjs.page.settings.loadImages"] = True
cap["phantomjs.page.settings.disk-cache"] = True

cap[
    "phantomjs.page.settings.userAgent"] = "Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:50.0) Gecko/20100101 Firefox/50.0",

cap[
    "phantomjs.page.customHeaders.User-Agent"] = 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:50.0) Gecko/20100101 Firefox/50.0',

def scroll(url, scroll_time):
    cap = webdriver.DesiredCapabilities.FIREFOX
    cap["phantomjs.page.settings.resourceTimeout"] = 1000
    cap["phantomjs.page.settings.loadImages"] = True
    cap["phantomjs.page.settings.disk-cache"] = True
    cap["phantomjs.page.settings.userAgent"] = "Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:50.0) Gecko/20100101 Firefox/50.0",
    cap["phantomjs.page.customHeaders.User-Agent"] = 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:50.0) Gecko/20100101 Firefox/50.0',

    # kname = quote(keyword)
    # url = "https://twitter.com/search?f=tweets&q={}&src=typd".format(kname)
    browser = webdriver.Firefox(desired_capabilities=cap)
    # browser = webdriver.PhantomJS(desired_capabilities=cap)
    browser.get(url)
    start = int(time.time())
    while 1:
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        end = int(time.time())
        if end - start == scroll_time:
            break
    html = browser.page_source
    with open('twitter.html', 'w') as f:
        f.write(html)
    browser.close()

def read_timest():
    f = open('twitter.html', 'rb')
    html = f.read()
    con = etree.HTML(html)
    """/li[last()]/div[@class="content"]/div[@class="stream-item-header"]/small/a/@data-original-title"""
    date = con.xpath('//div[@class="stream"]/ol[@id="stream-items-id"]/li[last()]//div[@class="content"]//small/a/@title')[0].decode('utf-8').split(" - ")[1]
    date = date.replace("年", '-').replace("月", '-').replace('日', '')
    Array = time.strptime(date, "%Y-%m-%d")
    timestamp = int(time.mktime(Array))
    print date
    return timestamp

def searchData(index, type ,body):
    query_body = {"query": {"query_string": {"query": body}}}
    results = es.search(index=index, doc_type=type, body=query_body)
    date_list = results['hits']['hits']
    return date_list

from langconv import *
#处理字体，把繁体转简体
def Traditional2Simplified(sentence):
    sentence = Converter('zh-hans').convert(sentence)
    return sentence


def crawl_twitter(url, start_strdate, end_strdate):
    start_timeArray = time.strptime(start_strdate, "%Y-%m-%d")
    start_timest = int(time.mktime(start_timeArray))
    end_timeArray = time.strptime(end_strdate, "%Y-%m-%d")
    end_timest = int(time.mktime(end_timeArray))

    # scroll_time = 300
    # scroll(url, scroll_time)
    # time.sleep(10)
    # timest = read_timest()
    # while timest >= start_timest:
    #     scroll_time += 200
    #     scroll(url, scroll_time)
    #     time.sleep(10)
    #     timest = read_timest()

    f = open('twitter.html', 'r')
    html = f.read()
    con = etree.HTML(html)
    #dates = con.xpath('//div[@class="content"]/div[1]/small[@class="time"]/a/span[1]/text()')
    lis = con.xpath('//ol[@id="stream-items-id"]/li')
    for li in lis:
        html = etree.tostring(li)
        item = {}
        retweet_count = ""
        favourites_count = ""
        # 昵称
        screen_name = li.xpath('.//strong[@class="fullname show-popup-with-id u-textTruncate "]/text()')
        # 内容
        text = ''.join(li.xpath('.//div[@class="content"]/div[2]/p//text()'))
        hash_md5 = hashlib.md5(text)
        Id = hash_md5.hexdigest()

        # 创建时间
        created_at = int(li.xpath('.//div[@class="content"]/div/small/a/span[1]/@data-time')[0])
        # if int(created_at) < 1514764800:
        #     break
        # 用户名
        user = '@' + li.xpath('.//div[@class="content"]/div[1]/a/span[2]/b/text()')[0]
        # twitter id
        id_tweet = li.xpath('./@data-item-id')[0]
        try:
            # 回复数
            retweet_count = int(li.xpath('.//div[@class="content"]/div[4]/div[2]/div[1]/button/span[@class="ProfileTweet-actionCount "]/span/text()')[0])
        except:
            retweet_count = 0
        try:
            # 赞数
            favourites_count = int(li.xpath('.//div[@class="content"]/div[4]/div[2]/div[3]/button/span/span/text()')[0])
        except:
            favourites_count = 0
        if retweet_count == "":
            retweet_count = 0
        if favourites_count == "":
            favourites_count = 0
        timesyear = time.localtime(created_at).tm_year
        stringDate = dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(created_at))
        # keyword = keyword.decode("utf-8")  # 关键词
        if created_at < start_timest:
            break
        if created_at >= start_timest and created_at <= end_timest:
        # keyword = Traditional2Simplified(keyword.decode("utf-8"))#关键词
            item['keyword'] = screen_name#关键词
            item['url'] = url  #昵称
            # item['screen_name'] = Traditional2Simplified(screen_name)  #昵称
            item['created_at'] = created_at     #创建时间
            item['text'] = text #内容
            # item['text'] = Traditional2Simplified(text).replace('\n','') #内容
            item['timesyear'] = timesyear   #年份
            item['comment'] = 0
            item['time'] = stringDate   #时间字符串
            item['id_tweet'] = id_tweet   #帖子的IDtwitter_id
            item['user'] = user   #用户名
            item['favourites_count'] = favourites_count #点赞数
            item['retweet_count'] = retweet_count   #回复数
            item['id'] = Id #md5值

            with open( 'Twitter_Germany.json', 'a') as f:
               f.write(json.dumps(item, ensure_ascii=False) + '\n')



if __name__ == '__main__':
    AngelaMerkel_url = 'https://twitter.com/Queen_Europe'
    HorstSeehofer_url = 'https://twitter.com/KoenigHorst'
    MartinSchulz_url = 'https://twitter.com/MartinSchulz'
    SahraWagenknecht_url = 'https://twitter.com/SWagenknecht'
    DietmarBartsch_url = 'https://twitter.com/DietmarBartsch'
    CemOzdemir_url = 'https://twitter.com/cem_oezdemir'
    KatrinGoringEckardt_url = 'https://twitter.com/GoeringEckardt'
    ChristianLindner_url = 'https://twitter.com/c_lindner'
    AlexanderGauland_url = 'https://twitter.com/alex_gauland'
    AliceWeidel_url = 'https://twitter.com/Alice_Weidel'


    # crawl_twitter(AngelaMerkel_url, '2017-03-01', '2017-09-24')
    # crawl_twitter(HorstSeehofer_url, '2017-03-01', '2017-09-24')
    # crawl_twitter(MartinSchulz_url, '2017-03-01', '2017-09-24')
    # crawl_twitter(SahraWagenknecht_url, '2017-03-01', '2017-09-24')
    crawl_twitter(DietmarBartsch_url, '2017-03-01', '2017-09-24')
    # crawl_twitter(CemOzdemir_url, '2017-03-01', '2017-09-24')
    # crawl_twitter(KatrinGoringEckardt_url, '2017-03-01', '2017-09-24')
    # crawl_twitter(ChristianLindner_url, '2017-03-01', '2017-09-24')
    # crawl_twitter(AlexanderGauland_url, '2017-03-01', '2017-09-24')
    # crawl_twitter(AliceWeidel_url, '2017-03-01', '2017-09-24')

