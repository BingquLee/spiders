#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-04-10 12:58:50
# @Author  : guangqiang_xu (981886190@qq.com)
# @Link    : http://www.treenewbee.com/
# @Version : $Id$

import requests
from elasticsearch import Elasticsearch
from lxml import etree
import time
from retry import retry
import re
import urllib, urllib2
import hashlib
from readability.readability import Document
import json
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

es = Elasticsearch()


def searchData(index, type, body):
    query_body = {"query": {"query_string": {"query": body}}}
    results = es.search(index=index, doc_type=type, body=query_body)
    date_list = results['hits']['hits']
    return date_list


from langconv import *


def Traditional2Simplified(sentence):
    sentence = Converter('zh-hans').convert(sentence)
    return sentence


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"}


@retry(tries=3)
def getcontent(dts, keyword, start_timest, end_timest):
    for dt in dts:
        news_url = dt.xpath('./a/@href')[0]
        date = dt.xpath('./a/span/text()')[0].split('：')[1]
        print date
        hash_md5 = hashlib.md5(news_url)
        Id = hash_md5.hexdigest()
        title = ''.join(dt.xpath('./a/h2//text()')).replace('\n', '')
        summary = ''.join(dt.xpath('./a/p//text()'))
        response = requests.get(news_url, headers=headers, timeout=20)
        response.coding = 'utf-8'
        txt = response.content
        news_html = etree.HTML(txt)
        readable_article = Document(txt).summary()
        art_html = etree.HTML(readable_article)
        context = ''.join(art_html.xpath('//p//text()')).replace('\n', '').replace('\r', '')
        # try:
        #     date = news_html.xpath('//div[@class="story_bady_info_author"]/span/text()')[0]
        # except:
        #     continue
        # print(date)
        try:
            timeArray = time.strptime(date, "%Y/%m/%d")
            timestamp = int(time.mktime(timeArray))
        except:
            pass
        print timestamp

        # if int(timestamp) < 1514764800:
        #     break
        timesyear = time.localtime(timestamp).tm_year
        stringDate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
        images = ''
        kname = urllib.quote(str(Traditional2Simplified(title)))
        try:
            Imageurl = "https://image.baidu.com/search/index?tn=baiduimage&ipn=r&ct=201326592&cl=2&lm=-1&st=-1&fm=result&fr=&sf=1&fmq=1502779395291_R&pv=&ic=0&nc=1&z=&se=1&showtab=0&fb=0&width=&height=&face=0&istype=2&ie=utf-8&word=" + kname
            req = urllib2.urlopen(Imageurl, timeout=10)
            html = req.read()
            images = re.search(r'https://.*?\.jpg', html).group()
        except:
            pass
        item = {}
        summary = Traditional2Simplified(summary.decode("utf-8"))
        keyword = Traditional2Simplified(keyword.decode("utf-8"))
        context = Traditional2Simplified(context.decode("utf-8")).replace('\r', '')
        title = Traditional2Simplified(title.decode("utf-8"))
        source = "联合新闻网"
        if timestamp < start_timest:
            break
        if timestamp >= start_timest and timestamp <= end_timest:
            item['summary'] = summary
            item['keyword'] = keyword
            item['candidate'] = keyword
            item['source'] = source
            item['timestamp'] = timestamp
            item['date'] = date
            item['lang'] = 'cn'
            item['images'] = images
            item['context'] = context
            item['timesyear'] = timesyear
            item['time'] = stringDate
            item['title'] = title
            item['url'] = news_url
            item['id'] = Id

            with open('lianhe_news.json', 'a') as f:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
            es.index(index="news", doc_type="fulltext", body=item)

            time.sleep(1)


def crawl_lianhe(keyword, start_strdate, end_strdate):
    kname = urllib.quote(str(keyword))
    page = 1

    start_timeArray = time.strptime(start_strdate, "%Y-%m-%d")
    end_timeArray = time.strptime(end_strdate, "%Y-%m-%d")
    start_timest = int(time.mktime(start_timeArray))
    end_timest = int(time.mktime(end_timeArray))

    while 1:
        url = "https://udn.com/search/result/2/{}/{}".format(kname, page)
        try:
            response = requests.get(url, headers=headers, timeout=20)
        except Exception as error:
            print error
        txt = response.text
        html = etree.HTML(txt)

        dts = html.xpath('//div[@id="search_content"]/dt')
        if len(dts) <= 0:
            break
        getcontent(dts, keyword, start_timest, end_timest)
        page += 1


if __name__ == '__main__':
    # crawl_lianhe('Viktor Orbán', '2017-11-01', '2018-04-08')
    # crawl_lianhe('Gergely Karácsony', '2017-11-01', '2018-04-08')
    # crawl_lianhe('Gábor Vona', '2017-11-01', '2018-04-08')
    # crawl_lianhe('Bernadett Szél', '2017-11-01', '2018-04-08')
    # crawl_lianhe('Ferenc Gyurcsány', '2017-11-01', '2018-04-08')
    crawl_lianhe('Viktor Szigetvári', '2017-11-01', '2018-04-08')


