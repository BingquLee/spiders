#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-21 16:43:13
# @Author  : guangqiang_xu (981886190@qq.com)
# @Version : $Id$

import os
import requests
from lxml import etree
from selenium import webdriver
from urllib import quote
import datetime
import time
import re
import hashlib
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

cap = webdriver.DesiredCapabilities.PHANTOMJS
cap["phantomjs.page.settings.resourceTimeout"] = 1000
cap["phantomjs.page.settings.loadImages"] = True
cap["phantomjs.page.settings.disk-cache"] = True

cap[
    "phantomjs.page.settings.userAgent"] = "Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:50.0) Gecko/20100101 Firefox/50.0",

cap[
    "phantomjs.page.customHeaders.User-Agent"] = 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:50.0) Gecko/20100101 Firefox/50.0',

def crawl_twitter(keyword, start_time, end_time):

    url = "https://twitter.com/{}".format(keyword)
    
    #browser = webdriver.PhantomJS(desired_capabilities=cap)
    browser = webdriver.Firefox()
    browser.get(url)
    time.sleep(3)
    pattern = re.compile('com\/(.*)')
    #候选人
    candidate = re.findall(pattern,url)[0]
    print(candidate)
    #关注者
    try:
        follower = browser.find_element_by_xpath('//ul[@class="ProfileNav-list"]/li[3]/a/span[3]').get_attribute("data-count")
    except:
        follower = browser.find_element_by_xpath('//ul[@class="ProfileNav-list"]/li[2]/a/span[3]').get_attribute("data-count")

    #喜欢
    try:
        like = browser.find_element_by_xpath('//ul[@class="ProfileNav-list"]/li[4]/a/span[3]').text
    except:
        like = 0
    start = int(time.time())
    while 1:
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        end = int(time.time())
        if end - start == 40:
            break
    todayStatus = []
    divs = browser.find_elements_by_xpath('//ol[@id="stream-items-id"]/li')
    for each in divs:
        try:
            dataItemId = each.get_attribute('data-item-id')
            statusUrl = url + "/status/" + dataItemId
            todayStatus.append({'tid':dataItemId,'url':statusUrl})
        except:
            pass
    
    browser = webdriver.Firefox()
    for status in todayStatus:
        try:
            statusDict = {}
            statusDict['candidate'] = candidate
            statusDict['follower'] = follower
            statusDict['like'] = like
            
            try:
                browser.get(status['url'])
                time.sleep(2)
            except:
                continue

            for each in browser.find_elements_by_xpath('//div[@class="permalink-inner permalink-tweet-container"]'):
                # 文本内容
                content = each.find_element_by_xpath('./div/div[2]').text
                # 发布时间
                statusTime = each.find_element_by_xpath('./div/div[4]/div/span/span').text
                if u'回复' in statusTime:
                    statusTime = each.find_element_by_xpath('./div/div[3]/div/span/span').text
                if u'上午' in statusTime:
                    statusTime = statusTime.split(' - ')[1].replace('年', '-').replace('月', '-').replace('日', '') + ' ' + statusTime.split(" - ")[0].replace('上午', '')            
                if u'下午' in statusTime:
                    date = str(int(statusTime.split(" - ")[0].split(':')[0].replace('下午', '')) + 12) + ':' + statusTime.split(" - ")[0].split(':')[0]
                    statusTime = statusTime.split(' - ')[1].replace('年', '-').replace('月', '-').replace('日', '') + ' ' + date.replace('下午', '')

                # 评论数
                try:
                    commentCount = each.find_element_by_xpath('./div/div[5]/div[2]/div[1]/button/span').text
                except:
                    try:
                        commentCount = each.find_element_by_xpath('./div/div[4]/div[2]/div[1]/button/span').text                
                    except:
                        try:
                            commentCount = each.find_element_by_xpath('./div/div[6]/div[2]/div[1]/button/span').text
                        except:
                            try:
                                commentCount = each.find_element_by_xpath('./div/div[5]/div[3]/div[1]/button/span').text
                            except:
                                try:
                                    commentCount = each.find_element_by_xpath('./div/div[6]/div[3]/div[1]/button/span').text
                                except:
                                    commentCount = each.find_element_by_xpath('./div/div[4]/div[3]/div[1]/button/span').text 

                try: 
                    commentLike = each.find_element_by_xpath('.//ul[@class="stats"]/li[2]/a').get_attribute('data-tweet-stat-count')
                except:
                    commentLike = '0'
                statusDict['content'] = content.replace('\n', '')
                statusDict['statusTime'] = statusTime
                statusDict['commentCount'] = commentCount
                statusDict['commentLike'] = commentLike
        

            commentList = []
            for each in browser.find_elements_by_xpath('//ol[@id="stream-items-id"]/li'):
                #try:
                if each.get_attribute('class').strip() == "ThreadedConversation--loneTweet":
                    info = {}
                    # uid
                    uid = each.find_element_by_xpath('./ol/li/div/div[2]/div[1]/a').get_attribute('data-user-id')
                    # 内容
                    try:
                        commentContent = each.find_element_by_xpath('./ol/li/div/div[2]/div[3]/p').text
                    except:
                        commentContent = each.find_element_by_xpath('./ol/li/div/div[2]/div[2]/p').text
                    # 时间
                    #commentTime = each.find_element_by_xpath('./ol/li/div/div[@class="content"]/div[1]/small/a/span').get_attribute('data-time')
                    commentTime = each.find_element_by_xpath('.//small[@class="time"]/a/span').get_attribute('data-time')
                    
                    # 点赞数
                    try:
                        commentLikeCount = each.find_element_by_xpath('./ol/li/div/div[2]/div[4]/div[2]/div[3]').text
                    except:
                        try:
                            commentLikeCount = each.find_element_by_xpath('./ol/li/div/div[2]/div[3]/div[2]/div[3]').text
                        except:
                            try:
                                commentLikeCount = each.find_element_by_xpath('./ol/li/div/div[2]/div[6]/div[2]/div[3]').text                   
                            except:
                                commentLikeCount = each.find_element_by_xpath('./ol/li/div/div[2]/div[5]/div[2]/div[3]').text


                    info['uid'] = uid
                    info['commentContent'] = commentContent
                    info['commentTime'] = commentTime
                    print commentTime
                    info['commentdate'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(commentTime)))
                    if commentLikeCount.replace('喜欢', '') == "":
                        info['commentLikeCount'] = 0
                    else:
                        try:
                            info['commentLikeCount'] = int(commentLikeCount.replace('喜欢', ''))
                        except:
                            info['commentLikeCount'] = 0
                    commentList.append(info)
                #except:
                elif each.get_attribute('class').strip() == "ThreadedConversation":
                    for e in each.find_elements_by_xpath('./ol/div'):
                        info = {}
                    # uid
                        uid = e.find_element_by_xpath('./li/div/div[2]/div[1]/a').get_attribute('data-user-id')
                        # 内容
                        try:
                            commentContent = e.find_element_by_xpath('./li/div/div[2]/div[3]/p').text
                        except:
                            commentContent = e.find_element_by_xpath('./li/div/div[2]/div[2]/p').text
                        # 时间
                        #commentTime = e.find_element_by_xpath('./ol/li/div/div[@class="content"]/div[1]/small/a/span').get_attribute('data-time')
                        commentTime = each.find_element_by_xpath('.//small[@class="time"]/a/span').get_attribute('data-time')
                        
                        # 点赞数
                        try:
                            commentLikeCount = e.find_element_by_xpath('./li/div/div[2]/div[4]/div[2]/div[3]').text
                        except:
                            try:
                                commentLikeCount = e.find_element_by_xpath('./li/div/div[2]/div[3]/div[2]/div[3]').text
                            except:
                                try:
                                    commentLikeCount = e.find_element_by_xpath('./li/div/div[2]/div[6]/div[2]/div[3]').text                 
                                except:
                                    commentLikeCount = e.find_element_by_xpath('./li/div/div[2]/div[5]/div[2]/div[3]').text

                        info['uid'] = uid
                        info['commentContent'] = commentContent
                        info['commentTime'] = commentTime
                        print commentTime
                        info['commentdate'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(commentTime)))
                        if commentLikeCount.replace('喜欢', '') == "":
                            info['commentLikeCount'] = 0
                        else:
                            try:
                                info['commentLikeCount'] = int(commentLikeCount.replace('喜欢', ''))
                            except:
                                info['commentLikeCount'] = 0
                        commentList.append(info)

            statusDict['commentList'] = commentList
            timeArray = time.strptime(statusDict['statusTime'], "%Y-%m-%d %H:%M")
            timestamp = int(time.mktime(timeArray))
            # 发表时间大于这个时间段不保存
            if timestamp>end_time:
                continue
            # 发表时间小于这个时间段直接退出
            if timestamp<start_time:
                break
            with open(keyword + '.json', 'a') as f:
                f.write(json.dumps(statusDict) + '\n')
            time.sleep(1)    
        except:
            continue

if __name__ == '__main__':
    # 起始日期
    start_time = 1488297600
    # 结束日期
    end_time = 1506182400
    keywords = ['KoenigHorst', 'MartinSchulz', 'SWagenknecht', 'DietmarBartsch','cem_oezdemir','GoeringEckardt','c_lindner','alex_gauland','Alice_Weidel']
    for keyword in keywords:
        crawl_twitter(keyword, start_time, end_time)

  