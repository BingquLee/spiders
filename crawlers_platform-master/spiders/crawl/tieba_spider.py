#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-04-27 09:19:51
# @Author  : guangqiang_xu (981886190@qq.com)
# @Version : $Id$

import requests
from lxml import etree
import json
import re
import urllib2
from urllib import quote
import os
import sys
from pybloom import BloomFilter
b = BloomFilter(10000000, 0.001)
from  retrying import retry
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append('../')
from crawl_xiciip import get_ip
from config import *
from log import spider_log
spider_name = 'tieba'
log_folder_name = '%s_logs' % spider_name
logger = spider_log(log_name=spider_name, log_folder_name=log_folder_name)
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}

#@retry()
def get_url(url,keyword):
    response = requests.get(url, headers=headers)
    logger.info('requests url: {}'.format(url))
    txt = response.text

    if re.search(r'<div class="s_post">.*?<div class="s_aside">', txt):
        text = re.search(r'<div class="s_post">.*?<div class="s_aside">', txt).group()
        txt = text.replace('<div class="s_aside">','')
        html = etree.HTML(txt)
        divs = html.xpath('//div[@class="s_post"]')
        for div in divs:
            url = div.xpath('./span[@class="p_title"]/a/@href')[0].split('?')[0]
            T = b.add(url)
            if T == True:
                continue
            get_content(div,keyword)
    else:
        pass


def save_img(path, img_id, url):
    try:
        picture = urllib2.urlopen(url).read()
    except urllib2.URLError, e:
        print e
        picture = False
    if picture:
        if not os.path.exists(path):  # 创建文件路径
            os.makedirs(path)
        f = open('%s/%s.jpg' % (path, img_id), "wb")
        f.write(picture)
        f.flush()
        f.close()

def get_content(div, keyword):
    url = "http://tieba.baidu.com" + div.xpath('./span[@class="p_title"]/a/@href')[0].split('?')[0]
    title = ''.join(div.xpath('./span[@class="p_title"]/a//text()')).replace('回复:','')
    tz_id = div.xpath('./span[@class="p_title"]/a/@data-tid')[0]
    tb_name =  div.xpath('./a[1]/font/text()')[0]
    user_name = div.xpath('./a[2]/font/text()')[0]
    strdate = div.xpath('./font[@class="p_green p_date"]/text()')[0]
    response = requests.get(url)
    txt = response.text
    html = etree.HTML(txt)
    fist_floor = html.xpath('//div[@id="j_p_postlist"]/div[1]')[0]

    content = fist_floor.xpath('.//cc/div')[0]
    info = {}
    if content.xpath('./img'):   # 判断是否有图片,有图片为true
        text = fist_floor.xpath('.//cc/div')[0].xpath('string(.)').strip()
        if len(text) == 0:
            return False  # 滤掉没有文字的帖子
        images = fist_floor.xpath('./div[3]/div[1]/cc/div/img')
        number = 1
        image_li = []
        for each in images:
            src = each.xpath('./@src')[0]
            if src.find('static')+1:  # 滤掉贴吧表情图片
                pass
            else:
                img_id = '%s_%s' % (tz_id, number)
                #save_img(tb_name, img_id, src)  # 保存图片到本地
                image_li.append('%s/%s_%s' % (tb_name, tz_id, number))
                number += 1
        info['content'] = text
        info['image'] = image_li
    else:
        info['content'] = ''.join(content.xpath('.//text()')).replace('\n', '').strip()
        info['image'] = ''

    info['source'] = tb_name
    info['title'] = title
    info['url'] = url
    data_field = fist_floor.xpath('./@data-field')[0]
    data_info = json.loads(data_field)
    try:
        info['createdate'] = data_info['content']['date']  # create time
    except:
        info['createdate'] = strdate
    try:
        info['sex'] = data_info['author']['user_sex']  # sex
    except:
        info['sex'] = ""
    info['author'] = data_info['author']['user_name']
    #reply_floor = html.xpath('//div[@class="l_post j_l_post l_post_bright  "]')
    reply_floor = html.xpath('//div[@id="j_p_postlist"]/div')
    reply_li = []
    for each_floor in reply_floor:
        if not each_floor.xpath('.//cc/div'):  # 滤掉百度推广
            return False
        reply_content = each_floor.xpath('.//cc/div')[0].xpath('string(.)').strip()
        reply_info = {}
        if len(reply_content) > 0:  # 滤掉无文字的回复
            re_field = each_floor.xpath('./@data-field')[0]
            re_info = json.loads(re_field)
            # reply_info['createdate'] = re_info['content']['date']
            reply_info['createdate'] = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2})", etree.tostring(each_floor)).group()
            reply_info['author'] = re_info['author']['user_name']
            reply_info['content'] = reply_content
            if reply_info['author'] == info['author']:
                continue
        reply_li.append(reply_info)
    info['reply'] = reply_li
    info['keyword'] = keyword

    with open('./tieba_data.json', 'a') as f:
        f.write(json.dumps(info, ensure_ascii=False) + '\n')

def main():
    page = 1
    for keyword in search_list:
        kname = quote(keyword)
        while 1:
            url = "http://tieba.baidu.com/f/search/res?isnew=1&kw=&qw={}&rn=10&un=&only_thread=0&sm=1&sd=&ed=&pn={}".format(kname, page)
            get_url(url,keyword)
            page += 1
            if page == 77:
                break    

if __name__ == '__main__':
    main()
