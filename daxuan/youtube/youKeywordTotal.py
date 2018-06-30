#!/usr/bin/env python
# encoding: utf-8
import json

from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# import requests
# import re
import time
# import json
# from pybloom import ScalableBloomFilter
# import pymongo
from pymongo import MongoClient
# from pyvirtualdisplay import Display
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

'''
1、候选人频道：
需要爬取的内容有： 候选人名字、日期、频道的订阅数、视频的标题、简介、每条视频的浏览次数、支持数、反对数，评论数、评论内容
每日更新一次。
2、以关键词命中的视频
需要爬取的内容有：                关键词、日期、视频的标题、简介、每条视频的浏览次数、支持数、反对数，评论数、评论内容 
'''

#模拟窗口
#display = Display(visible=0,size=(1024,768))
#display.start()
# firefoxProfile = webdriver.FirefoxProfile()
# firefoxProfile.set_preference('permissions.default.stylesheet',2)
# firefoxProfile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so','false')
# firefoxProfile.set_preference('permissions.default.image',2)
# driver = webdriver.Firefox(firefox_profile=firefoxProfile)

driver = webdriver.Firefox()

#连接数据库
client = MongoClient('219.224.134.212',27017)
db = client.youtube

keyword_list = []
with open('keyword.txt','r+') as f:
    for k in f.readlines():
        k = k.strip()
        keyword_list.append(k)

for keyword in keyword_list:
    print(keyword)
    keyword = keyword.replace(' ','+')
    url = 'https://www.youtube.com/results?search_query=' + keyword
    driver.get(url)
    time.sleep(20)

#加载更多
    length=100
    for i in range(0,500):
        js="var q=document.documentElement.scrollTop="+str(length)
        driver.execute_script(js)
        time.sleep(2)
        length += 400

    video_list = []	#视频列表
    for each in driver.find_elements_by_xpath('//ytd-video-renderer[@class="style-scope ytd-item-section-renderer"]'):
        try:
            videoUrl = each.find_element_by_xpath('./div/div/div/div/h3/a').get_attribute('href')
            video_list.append(videoUrl)	#当天视频放入视频列表
        except Exception as e:
            print "1111111111111111111", e
            pass

#进入视频页
    for videoUrl in video_list:
        try:
            print(videoUrl)
            driver.get(videoUrl)
            time.sleep(3)

            #标题
            try:
                title = driver.find_element_by_xpath('//div[@id="info"]/div[2]/ytd-video-primary-info-renderer/div/h1').text
            except BaseException, e:
                print "22222222222222", e
                title = 'None'
            try:
                driver.find_element_by_xpath('//div[@id="meta"]/div[3]/ytd-video-secondary-info-renderer/div[1]/ytd-expander/paper-button[2]').click()
            except:
                pass
            #简介
            try:
                description = driver.find_element_by_xpath('//div[@id="meta"]/div[3]/ytd-video-secondary-info-renderer/div[1]/ytd-expander').text
            except:
                description = 'None'
            #发布时间
            try:
                # date = driver.find_element_by_xpath('//div[@id="meta"]/div[3]/ytd-video-secondary-info-renderer/div[1]/div[2]/ytd-video-owner-renderer/div[1]/span').text.replace(u'发布','')
                date = driver.find_element_by_xpath('//span[@slot="date"]').text.replace(u"发布","")
            except:
                date = 'None'
            #观看数量
            try:
                viewCount = driver.find_element_by_xpath('//div[@id="info"]/div[2]/ytd-video-primary-info-renderer/div/div/div[1]').text
            except:
                viewCount = 'None'
            #赞成数
            try:
                For = driver.find_element_by_xpath('//div[@id="info"]/div[2]/ytd-video-primary-info-renderer/div/div/div[3]/div[1]/ytd-menu-renderer/div[1]/ytd-toggle-button-renderer[1]').text
            except:
                For = 'None'
            #反对数
            try:
                against = driver.find_element_by_xpath('//div[@id="info"]/div[2]/ytd-video-primary-info-renderer/div/div/div[3]/div[1]/ytd-menu-renderer/div[1]/ytd-toggle-button-renderer[2]').text
            except:
                against = 'None'

            #加载更多
            length=100
            for i in range(0,10):
                js="var q=document.documentElement.scrollTop="+str(length)
                driver.execute_script(js)
                time.sleep(2)
                length += 100

            #评论数
            try:
                commentCount = driver.find_element_by_xpath('//ytd-comments[@id="comments"]/ytd-item-section-renderer/div[1]/ytd-comments-header-renderer/div[1]/h2').text
            except:
                commentCount = 'None'

            #评论内容
            content_list = []
            try:
                for each in driver.find_elements_by_xpath('//ytd-comments[@id="comments"]/ytd-item-section-renderer/div[2]/ytd-comment-thread-renderer'):
                    #点击“查看回复”
                    try:
                        each.find_element_by_xpath('./div/ytd-comment-replies-renderer/ytd-expander/paper-button').click()
                    except:
                        pass
                    content = each.find_element_by_xpath('./ytd-comment-renderer/div/div[2]/ytd-expander/div').text
                    content_list.append(content)
            except:
                pass

            dict = {'keyword':keyword.encode('utf-8'), 'url':videoUrl, 'publish_time':date, 'title':title, 'description':description.encode("utf-8"), 'viewCount':viewCount, 'For':For, 'against':against, 'commentCount':commentCount, 'content_list':content_list}

            # db.new_youKeyword_total.insert(dict)
            with open("Viktor_Orban.json", "a") as f:
                f.write(json.dumps(dict, ensure_ascii=False) + "\n")
        except Exception as e:
            pass
        time.sleep(1)

'''
Luigi Di Maio
M5S

'''


