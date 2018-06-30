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

def crawl_twitter(keyword):
    kname = quote(keyword)
    url = "https://twitter.com/search?f=tweets&q={}&src=typd".format(kname)
    #browser = webdriver.Firefox()
    browser = webdriver.PhantomJS(desired_capabilities=cap)
    browser.get(url)
    start = int(time.time())
    while 1:
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        end = int(time.time())
        if end - start == 150:
            break

    html = browser.page_source
    with open('twitter.html', 'w') as f:
        f.write(html)

    browser.close()

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
        screen_name = li.xpath('.//strong[@class="fullname show-popup-with-id u-textTruncate "]/text()')[0]
        # 内容
        text = ''.join(li.xpath('.//div[@class="content"]/div[2]/p//text()'))
        hash_md5 = hashlib.md5(text)
        Id = hash_md5.hexdigest()

        # 创建时间
        created_at = int(li.xpath('.//div[@class="content"]/div/small/a/span[1]/@data-time')[0])
        if int(created_at) < 1514764800:
            break
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
        keyword = Traditional2Simplified(keyword.decode("utf-8"))#关键词
        item['keyword'] = keyword#关键词
        item['screen_name'] = Traditional2Simplified(screen_name)  #昵称
        item['created_at'] = created_at     #创建时间
        item['text'] = Traditional2Simplified(text).replace('\n','') #内容
        item['timesyear'] = timesyear   #年份
        item['comment'] = 0
        item['time'] = stringDate   #时间字符串
        item['id_tweet'] = id_tweet   #帖子的IDtwitter_id
        item['user'] = user   #用户名
        item['favourites_count'] = favourites_count #点赞数
        item['retweet_count'] = retweet_count   #回复数
        item['id'] = Id #md5值
        
        with open( 'twitter.json', 'a') as f:
           f.write(json.dumps(item, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    crawl_twitter('Mostafa Hashemitaba')
    crawl_twitter('Ebrahim Raisi')
    crawl_twitter('Hassan Rouhani')
    crawl_twitter('Mostafa Mir-Salim')

