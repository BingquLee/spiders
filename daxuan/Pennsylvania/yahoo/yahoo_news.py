#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-04-11 14:45:12
# @Author  : guangqiang_xu (981886190@qq.com)
# @Link    : http://www.treenewbee.com/
# @Version : $Id$

import requests
from lxml import etree
from retry import retry
import time
import json
import hashlib
import re
import urllib, urllib2
from readability.readability import Document
from elasticsearch import Elasticsearch
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

es = Elasticsearch()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"}


def searchData(index, type ,body):
    query_body = {"query": {"query_string": {"query": body}}}
    results = es.search(index=index, doc_type=type, body=query_body)
    date_list = results['hits']['hits']
    return date_list


from langconv import *

def Traditional2Simplified(sentence):
    sentence = Converter('zh-hans').convert(sentence)
    return sentence

@retry(tries=3)
def get_content(lis, keyword, timest):
    i = 1
    for li in lis:
        item = {}
        source = "yahoo"
        news_url = li.xpath('./div/div[1]/h3/a/@href')[0]
        title = ''.join(li.xpath('./div/div[1]/h3/a//text()'))
        summary = ''.join(li.xpath('./div/div[2]/p//text()'))
        user_name = li.xpath('./div/div[3]/p/span[1]/text()')[0]
        date = li.xpath('./div/div[3]/p/span[2]/text()')[0]
        strdate = '2018-' + date.replace('AM','').replace('PM','').replace('月','-').replace('日','')
        timeArray = time.strptime(strdate, "%Y-%m-%d %H:%M")
        timestamp = int(time.mktime(timeArray))
        if timestamp < timest:
            continue
        response1 = requests.get(news_url, timeout=10, headers=headers)
        response1.coding = 'utf-8'
        txt1 = response1.content
        new_url = re.findall(r'URL=(.*?)">',txt1)[0].replace("'",'')
        hash_md5 = hashlib.md5(new_url)
        Id = hash_md5.hexdigest()
        response = requests.get(new_url, timeout=10, headers=headers)
        response.coding = 'utf-8'
        txt = response.content   
        readable_article = Document(txt).summary()
        html = etree.HTML(readable_article)
        context = ''.join(html.xpath('//p//text()')).replace('\r','').replace('\n','').replace('\t','')
        if context in "":
            news_html = etree.HTML(txt)
            context = ''.join(news_html.xpath('//p//text()'))
        timesyear = time.localtime(timestamp).tm_year
        stringDate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
        images = ''
        kname = urllib.quote(str(title))
        try:
            Imageurl = "https://image.baidu.com/search/index?tn=baiduimage&ipn=r&ct=201326592&cl=2&lm=-1&st=-1&fm=result&fr=&sf=1&fmq=1502779395291_R&pv=&ic=0&nc=1&z=&se=1&showtab=0&fb=0&width=&height=&face=0&istype=2&ie=utf-8&word=" + kname
            req = urllib2.urlopen(Imageurl, timeout=10)
            html = req.read()
            images = re.search(r'https://.*?\.jpg', html).group()
        except:
            pass

        summary = Traditional2Simplified(summary.decode("utf-8"))
        keyword = Traditional2Simplified(keyword.decode("utf-8"))
        context = Traditional2Simplified(context.decode("utf-8"))
        tittle = Traditional2Simplified(title.decode("utf-8"))

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
        item['title'] = tittle
        item['url'] = new_url
        item['id'] = Id
        
        with open('yahoo_news.json', 'a') as f:
             f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
        
def crawl_yahoo(keyword, strdate):
    timeArray = time.strptime(strdate, "%Y-%m-%d")
    timest = int(time.mktime(timeArray))
    kname = urllib.quote(str(keyword))
    page = 1
    while 1:
        url = "https://tw.news.search.yahoo.com/search;_ylt=AwrtXGtDr81aAG4A2CVw1gt.;_ylu=X3oDMTEwOG1tc2p0BGNvbG8DBHBvcwMxBHZ0aWQDBHNlYwNwYWdpbmF0aW9u?p={}&ei=UTF-8&flt=ranking%3Adate%3B&fr=yfp-search-sb&b={}&pz=10&bct=0&xargs=0".format(kname, page)
        print url
        response = requests.get(url, headers=headers)
        txt = response.text
        html = etree.HTML(txt)
        lis = html.xpath('//div[@id="web"]/ol[2]/li')
        if len(lis) <= 0:
            break
        get_content(lis, keyword, timest)
        page += 10
        if page == 81:
            break


if __name__ == '__main__':

    # crawl_yahoo('Mostafa Hashemitaba', '2017-01-01')
    # crawl_yahoo('Ebrahim Raisi', '2017-01-01')
    # crawl_yahoo('Hassan Rouhani', '2017-01-01')
    # crawl_yahoo('Mostafa Mir-Salim', '2017-01-01')
    crawl_yahoo('Conor Lamb', '2017-10-01')
    crawl_yahoo('Drew Gray Miller', '2017-10-01')
