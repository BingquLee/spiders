#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-04-11 13:52:58
# @Author  : guangqiang_xu (981886190@qq.com)
# @Link    : http://www.treenewbee.com/
# @Version : $Id$

import requests
from lxml import etree
import time
from retry import retry
import re
import urllib, urllib2
import hashlib
from readability.readability import Document
import json
import sys
from elasticsearch import Elasticsearch
reload(sys)
sys.setdefaultencoding('utf-8')

es = Elasticsearch()


def searchData(index, type ,body):
    query_body = {"query": {"query_string": {"query": body}}}
    es.indices.create(index=index)
    results = es.search(index=index, doc_type=type, body=query_body)
    date_list = results['hits']['hits']
    return date_list

from langconv import *

def Traditional2Simplified(sentence):
    sentence = Converter('zh-hans').convert(sentence)
    return sentence


@retry(tries=3)
def getcontent(divs, keyword, start_timest, end_timest):
    for div in divs:
        source = "东森新闻云"
        timestamp = ""
        news_url = div.xpath('./div[@class="box_2"]/h2/a/@href')[0]
        hash_md5 = hashlib.md5(news_url)
        Id = hash_md5.hexdigest()
        title = ''.join(div.xpath('./div[@class="box_2"]/h2/a//text()'))
        summary = ''.join(div.xpath('./div[@class="box_2"]/p//text()'))
        date = div.xpath('./div[@class="box_2"]/p/span/text()')[1].replace(' / ','').replace(')','')
        timeArray = time.strptime(date, "%Y-%m-%d %H:%M")
        timestamp = int(time.mktime(timeArray))
        # if timestamp < timest:
        #     continue
        response = requests.get(news_url, timeout=15)
        response.coding = 'utf-8'
        txt = response.content
        readable_article = Document(txt).summary()
        html = etree.HTML(readable_article)
        context = ''.join(html.xpath('//p//text()')).replace('\n', '')
        timesyear = time.localtime(timestamp).tm_year
        stringDate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
        images = ''
        news_html = etree.HTML(txt)
        try:
            images = 'https:' + news_html.xpath('//div[@class="story"]//img/@src')[0]
        except:
            kname = urllib.quote(str(title))
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
        if timestamp <= start_timest:
            break
        if timestamp >=start_timest and timestamp <= end_timest:
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
            es.index(index="news", doc_type="fulltext", body=item)

            with open('yun_news.json', 'a') as f:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')

            time.sleep(1)

def crawl_yun(keyword, start_strdate, end_strdate):
    page = 1
    start_timeArray = time.strptime(start_strdate, "%Y-%m-%d")
    end_timeArray = time.strptime(end_strdate, "%Y-%m-%d")
    start_timest = int(time.mktime(start_timeArray))
    end_timest = int(time.mktime(end_timeArray))
    kname = urllib.quote(str(keyword))
    while 1:
        url = "https://www.ettoday.net/news_search/doSearch.php?keywords={}&idx=1&page={}".format(kname, page)
        print url
        response = requests.get(url)
        txt = response.text
        html = etree.HTML(txt)
        divs = html.xpath('//div[@id="result-list"]/div[@class="archive clearfix"]')
        if len(divs) <= 0:
            break
        getcontent(divs, keyword, start_timest, end_timest)
        page += 1



if __name__ == '__main__':
    crawl_yun('Emmanuel Macron', '2017-01-01', '2017-05-07')
    crawl_yun('Marine Le Pen', '2017-01-01', '2017-05-07')