#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-18 13:36:33
# @Author  : guangqiang_xu (981886190@qq.com)
# @Version : $Id$

from __future__ import unicode_literals
import youtube_dl
import json
import requests
from lxml import etree
import os
from selenium import webdriver
from lxml import etree
import time


import sys
reload(sys)
sys.setdefaultencoding('utf-8')

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"}
sess = requests.session()


def _get_youtube_video_info(url):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url)


def get_youtube_video_data(urls, keyword):
    for url in urls:
        item = {}
        if "watch?" not in url:
            continue
        video_url = 'https://www.youtube.com' + url
        data = _get_youtube_video_info(video_url)
        stringdate = data['upload_date']
        timeArray = time.strptime(stringdate, "%Y%m%d")
        timestamp = int(time.mktime(timeArray))
        if timestamp < 1506787200 or timestamp > 1520438400:
            continue
        # browser = webdriver.PhantomJS(desired_capabilities=cap)
        browser = webdriver.Firefox()
        try:
            browser.get(video_url)
        except:
            continue
        time.sleep(10)
        start = int(time.time())
        length=100
        for i in range(0,30):
            js="var q=document.documentElement.scrollTop="+str(length)
            browser.execute_script(js)
            print(js)
            time.sleep(2)
            length += 1800

        txt = browser.page_source
        html = etree.HTML(txt)
        stringdate = data['upload_date']
        timeArray = time.strptime(stringdate, "%Y%m%d")
        timestamp = int(time.mktime(timeArray)) 
        strDate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))       
        divs = html.xpath('//div[@id="contents"]/ytd-comment-thread-renderer')
        comments = []
        for div in divs:
            try:
                info = {}
                info['user_name'] = div.xpath('.//a[@id="author-text"]/span/text()')[0].strip()
                info['content'] = div.xpath('.//div[@id="content"]/yt-formatted-string[@id="content-text"]/text()')[0].strip()
                strdate = div.xpath('.//yt-formatted-string[@id="published-time-text"]/a/text()')[0].strip()
                if '个月前' in strdate:
                    num = int(strdate.replace(' 个月前', ''))
                    date = num * 30
                    timea = time.time()
                    info['timestamp'] = timea - date*86400
                    info['times'] = stringDate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(info['timestamp']))
                elif '周前' in strdate:
                    num = int(strdate.replace('周前', ''))
                    date = num * 7
                    timea = int(time.time())
                    info['time'] = stringDate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timea - date*86400))
                elif '天前' in strdate:
                    num = int(strdate.replace('周前', ''))
                    date = num * 86400
                    info['time'] = stringDate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timea - date))
                elif '小时前' in strdate:
                    num = int(strdate.replace('小时前', ''))
                    date = num * 3600
                    info['time'] = stringDate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timea - date))
                elif '分钟前' in strdate:
                    num = int(strdate.replace('分钟前', ''))
                    date = num * 60
                    info['time'] = stringDate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timea - date))

                comments.append(info)

            except:
                continue
        item['title'] = data['title']
        try:
            item['summary'] = data['description']
        except:
            item['summary'] = ''
        item['view_count'] = data['view_count']
        item['like_count'] = data['like_count']
        item['dislike_count'] = data['dislike_count']
        item['time'] = strDate
        item['timestamp'] = timestamp
        item['comments'] = comments
        item['id'] = data['id']

        with open(keyword + '.json', 'a') as f:
            f.write(json.dumps(item)+'\n')
        browser.close()
def get_url(keyword):
    page = 1
    while 1:
        url = "https://www.youtube.com/results?search_query={}&sp=CAI%253D&page={}".format(keyword, page)
        response = sess.get(url,headers=headers)
        txt = response.text
        html = etree.HTML(txt)
        urls = html.xpath('//h3/a/@href')
        if len(urls) <= 0:
            break
        get_youtube_video_data(urls, keyword)

if __name__ == '__main__':
    keywords = ["Влади́мир Влади́мирович Пу́тин", "Ксе́ния Анато́льевна Собча́к", "Павел Гружинин", "Влади́мир Во́льфович Жирино́вский", "Алексе́й Анато́льевич Нава́льный"]
    for i in keywords:
        get_url(i)
    