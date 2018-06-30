#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-04-25 18:14:59
# @Author  : guangqiang_xu (981886190@qq.com)
# @Version : $Id$

import requests
from hashlib import sha1
# import http.cookiejar as cookielib
import time
import hmac
import json
import re
from lxml import etree
from  retrying import retry
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append('../')
from crawl_xiciip import get_ip
from config import *
from log import spider_log

spider_name = 'zhihu'
log_folder_name = '%s_logs' % spider_name
logger = spider_log(log_name=spider_name, log_folder_name=log_folder_name)

class ZhiHuLogin(object):
    
    def __init__(self, username, password, 
                 client_id='c3cef7c66a1843f8b3a9e6a1e3160e20',
                 key='d1b964811afb40118a12068ff74a12f4'):
        
        self.login_url = 'https://www.zhihu.com/signup?next=%2F'
        self.captcha_url = 'https://www.zhihu.com/api/v3/oauth/captcha?lang=cn'
        self.sign_in_url = 'https://www.zhihu.com/api/v3/oauth/sign_in'
        self.captcha_flag = 1
        self.sess = None
        self.key = key
        self.log = logger
        self.form_data = {}
        self.form_data['username'] = username
        self.form_data['password'] = password
        self.form_data['client_id'] = client_id
        self.form_data['grant_type'] = 'password'
        self.form_data['source'] = 'com.zhihu.web'
        self.form_data['captcha'] = None
        self.form_data['lang'] = 'en'
        self.form_data['ref_source'] = 'homepage'
        self.form_data['utm_source'] = None
        self.form_data['timestamp'] = str(int(time.time()))
        
        self.headers = self.get_headers()
    
        
    def get_headers(self):
        
        return {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0','HOST':'www.zhihu.com',\
           'Referer':'https://www.zhihu.com/signin?next=%2F','Authorization':'oauth c3cef7c66a1843f8b3a9e6a1e3160e20'}

    def get_sess(self):
        
        i = 1
        while self.captcha_flag:
            
            self.log.info('开始尝试第{}次'.format(i))
            i += 1
            
            self.headers = self.get_headers()
            self.sess = requests.Session()
            # self.sess.cookies = cookielib.LWPCookieJar(filename = 'cookies_res.txt')
            response = self.sess.get(self.login_url, headers=self.headers)
            try:
                x_udid = re.findall(r'{&quot;xUDID&quot;:&quot;([^;&]*)&quot;}',
                                   response.text)[0]
                if not x_udid:
                   continue
                self.headers['x-udid'] = x_udid
            except:
                pass
            cap_response = self.sess.get(self.captcha_url, 
                                       headers=self.headers, verify=True)
            dic = json.loads(cap_response.text)
            self.log.info('请求参数： '.format(dic))
            if not dic['show_captcha']:
                self.captcha_flag = 0
        return True

    def get_captcha(self):
        try:
            # 获取验证码图片
            self.headers = self.get_headers()
            self.sess = requests.Session()        
            t = str(int(time.time() * 1000))
            captcha_url = "https://www.zhihu.com/captcha.gif?r={0}&type=login".format(t)
            t = self.sess.get(captcha_url, headers=self.headers)
            with open("zhihu_captcha.jpg", "wb") as f:
                f.write(t.content)

            try:
                from PIL import Image
                im = Image.open("zhihu_captcha.jpg")
                im.show()
                im.close()
            except:
                pass
        except Exception as error:
            self.log.error('获取验证码失败: {}'.format(error))

        captcha = raw_input("输入验证码：")
        return captcha
    # 计算 signature 值
    def get_signature(self):
        
        myhmac = hmac.new(self.key, digestmod=sha1)
        myhmac.update(bytes(self.form_data['grant_type']))
        myhmac.update(bytes(self.form_data['client_id']))
        myhmac.update(bytes(self.form_data['source']))
        myhmac.update(bytes(self.form_data['timestamp']))
        return myhmac.hexdigest()

    def get_data(self,data,keyword):
        for d in data:
            item = {}

            try:
                question_title = d['object']['question']['name']
            except:
                try:
                    question_title = d['highlight']['title']
                except:
                    continue

            try:
                question_id = d['object']['question']['id']
            except:
                question_id = ""
            try:
                question_type = d['object']['question']['type']
            except:
                question_type = ""
            try:
                content_summary = d['object']['excerpt']
            except:
                content_summary = ""
            try:
                up_content = d['object']['content']
            except:
                up_content = ""
            try:
                up_author_name = d['object']['author']['name']
            except:
                up_author_name = ""
            try:
                up_author_url = 'https://www.zhihu.com/people/' + d['object']['author']['url_token']
            except:
                up_author_url = ""
            try:
                up_author_headline = d['object']['author']['headline']
            except:
                up_author_headline = ""
            try:
                up_comment_count = d['object']['comment_count']
            except:
                up_comment_count = ""
            try:
                up_create_time = d['object']['created_time']
            except:
                up_create_time = ""
            try:
                up_voteup_count = d['object']['voteup_count']
            except:
                up_voteup_count = ""
            try:
                up_update_time = d['object']['updated_time']
            except:
                up_update_time = ""
                
            # 帖子标题
            item['question_title'] = question_title
            # 帖子id
            item['question_id'] = question_id
            # 帖子链接
            item['question_url'] = 'https://www.zhihu.com/question/' + question_id            
            # 帖子类型
            item['question_type'] = question_type
            # 最高答案得赞数
            item['up_voteup_count'] = up_voteup_count
            # 回答赞数最高帖子摘要
            item['content_summary'] = content_summary
            # 回答赞数最高帖子内容
            item['up_content'] = up_content
            # 回答赞数最高的用户昵称
            item['up_author_name'] = up_author_name
            # 回答赞数最高的用户个人主页
            item['up_author_url'] = up_author_url
            # 回答赞数最高的用户个人简介
            item['up_author_headline'] = up_author_headline
            # 回答赞数最高答案的评论数
            item['up_comment_count'] = up_comment_count
            # 赞数最高答案的创建时间
            item['up_create_time'] = up_create_time
            # 赞数最高答案的最后更新时间
            item['up_update_time'] = up_update_time

            item['keyword'] = keyword

            with open('./ZhiHu.json', 'a') as f:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')

    def sign_in(self):
        item = {}
        signature = self.get_signature()
        self.form_data['signature'] = signature
        self.form_data['captcha'] = self.get_captcha()
        #self.get_sess()
        # print self.form_data
        self.sess.post(self.sign_in_url, data=self.form_data, 
                                  headers=self.headers)
        # self.sess.cookies.save(ignore_expires=True,ignore_discard=True)
        # page URL
        # https://www.zhihu.com/api/v4/search_v3?t=general&q=%E5%9C%9F%E8%80%B3%E5%85%B6&correction=1&offset=35&limit=10&search_hash_id=f4404ae2ce377b03c1ec63796a153b35
        # 以土耳其为关键字的url
    
        
        for keyword in search_list:
            limit = 10
            offset = 0            
            query_key = keyword
            basic_url = "https://www.zhihu.com/api/v4/search_v3?t=general&q=%s&correction=1" \
                        "&search_hash_id=4507b273793a743841253e912a8edf5e&offset=%s&limit=%s"

            while 1:
                url = basic_url % (query_key, offset, limit)
                response = self.sess.get(url, headers=self.headers)
                response_rm_em = response.content.decode("utf-8").replace("<em>", "").replace("<\/em>", "")
                data = json.loads(response_rm_em)['data']
                if len(data) == 0:
                    self.log.info('关键词：{} 爬取结束！')
                    break
                self.get_data(data,keyword)
                self.log.info('request {}, page: {}'.format(url, offset/10 + 1))
                offset += limit
                time.sleep(1)

login = ZhiHuLogin(zh_username, zh_password)


if __name__=="__main__":

    login = ZhiHuLogin(zh_username, zh_password)
    login.sign_in()