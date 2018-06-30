#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-07 19:11:47
# @Author  : guangqiang_xu (981886190@qq.com)
# @Link    : http://www.treenewbee.com/
# @Version : $Id$

import requests
import urllib
from lxml import etree
import datetime
import time
import json
import re
from elasticsearch import Elasticsearch
import sys
import urllib3
urllib3.disable_warnings()
reload(sys)
sys.setdefaultencoding('utf-8')

from langconv import *

es = Elasticsearch()

def Traditional2Simplified(sentence):
    sentence = Converter('zh-hans').convert(sentence)
    return sentence

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
date_item = {"Jan": "1", "Feb": "2", "Mar": "3", "Apr": "4", "May": "5", "Jun": "6", "Jul": "7", 
            "Aug": "8", "Sep": "9", "Oct": "10", "Nov": "11", "Dec": "12", }

load={
'from':'/bbs/Gossiping/index.html',
'yes':'yes' 
}

sess = requests.session()

def searchData(index, type ,body):
    query_body = {"query": {"query_string": {"query": body}}}
    results = es.search(index=index, doc_type=type, body=query_body)
    date_list = results['hits']['hits']
    return date_list

def ip_home(ip):
    try:
        url = "http://www.ip138.com/ips138.asp?ip={}&action=2".format(ip)
        response = requests.get(url)
        response.coding = 'utf-8'
        txt = response.content
        html = etree.HTML(txt)
        ip_h = html.xpath('//ul[@class="ul1"]/li[1]/text()')[0].split(u'：')[1].strip()
    except:
        ip_h = u'台湾省'

    return ip_h

def get_content(urls, keyword):
    for url in urls:
        url = 'https://www.ptt.cc' + url
        try:
            response = sess.get(url, headers=headers, verify=False)
        except:
            continue
        if response.status_code == 404 or response.status_code == 524:
            continue
        response.coding = 'utf-8'
        txt = response.content
        html = etree.HTML(txt)
        item = {}

        author = html.xpath('//div[@id="main-content"]/div[1]/span[2]/text()')[0]
        title = html.xpath('//div[@id="main-content"]/div[3]/span[2]/text()')[0]
        date = html.xpath('//div[@id="main-content"]/div[4]/span[2]/text()')[0]
        ip = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", txt)[0]
        content = ''.join(html.xpath('//div[@id="main-content"]//text()')).split(date)[1].split(ip)[0].replace(', 來自: ','')
        pushs = html.xpath('//div[@id="main-content"]/div[@class="push"]')
        Id = url.split('/')[-1].replace('.html', '')
        search_list = searchData("_all", "fulltext", "id:{}".format(Id))
        if len(search_list) > 0:
            continue 
        push_list = []
        user_list = []
        push_num = 0
        dispush_num = 0 
        neutral_num = 0
        ds = date.replace('  ',' ').split(' ')
        for p in pushs:
            info = {}
            push = p.xpath('./span[1]/text()')[0].strip()
            # info['push'] = push
            info['id'] = Id
            info['author'] = p.xpath('./span[2]/text()')[0]
            push_content = p.xpath('./span[3]/text()')[0].replace(': ','')
            info['context'] = Traditional2Simplified(push_content)
            strdt = ds[-1] + '-' + p.xpath('./span[4]/text()')[0].replace('/','-').replace('\n', '').strip()
            if info['context'] in "":
                continue
            try:
                timeArray = time.strptime(strdt, "%Y-%m-%d %H:%M")
            except:
                continue
            timestamp = int(time.mktime(timeArray)) 
            info['time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp)) 
            info['timestamps'] = timestamp
            if push in "推":
                push_num += 1
                info['status'] = 2
            elif push in "噓":
                dispush_num += 1
                info['status'] = 0
            elif push in "→":
                neutral_num += 1
                info['status'] = 1

            push_list.append(info)
            user_list.append(info['author'])

        sdate = ds[-1] + '-' + date_item[ds[1]] + '-' + ds[2] + ' ' + ds[3]
        timeArray = time.strptime(sdate, "%Y-%m-%d %H:%M:%S")
        timestamp = int(time.mktime(timeArray))
        stringDate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
        keyword = Traditional2Simplified(keyword.decode('utf-8'))
        author = Traditional2Simplified(author)
        title = Traditional2Simplified(title)
        context = Traditional2Simplified(content.replace('\n',' '))

        item['keywords'] = keyword
        item['id'] = Id
        item['author'] = author
        item['title'] = title
        item['time'] = stringDate
        item['source'] = 'ptt'
        item['likes'] = push_num
        item['tread'] = dispush_num
        item['buddha_operation'] = neutral_num
        item['comments'] = len(push_list)
        item['reviews'] = len(set(user_list))
        item['context'] = context
        item['address'] = ip_home(ip)
        item['push'] = push_list

        # item['url'] = url
        item['timestamps'] = timestamp

        with open('ptt_news.json', 'a') as f:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
        

def crawl_ptt(keyword):
    page = 1
    while 1:
        sess.post('https://www.ptt.cc/ask/over18', verify=False, data=load)
        kname = urllib.quote(keyword)
        url = "https://www.ptt.cc/bbs/Gossiping/search?page={}&q={}".format(page, kname)
        response = sess.get(url, headers=headers)
        if response.status_code == 404:
            break
        txt = response.text
        html = etree.HTML(txt)
        urls = html.xpath('//div[@class="title"]//a/@href')
        get_content(urls, keyword)
        # for url in urls:
        #     news_url = 'https://www.ptt.cc' + url
        #     get_content(news_url, keyword)
            # time.sleep(2)
        page += 1

if __name__ == '__main__':
    crawl_ptt('Mostafa Hashemitaba')
    crawl_ptt('Ebrahim Raisi')
    crawl_ptt('Hassan Rouhani')
    crawl_ptt('Mostafa Mir-Salim')