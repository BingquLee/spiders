#coding:utf-8
import requests
import random
import json
import re
import time
from lxml import etree
from readability.readability import Document
from  retrying import retry
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append('../')
from crawl_xiciip import get_ip
from config import *
from urllib import quote
session = requests.session()
from log import spider_log

spider_name = 'sina'
log_folder_name = '%s_logs' % spider_name
logger = spider_log(log_name=spider_name, log_folder_name=log_folder_name)

user_agents = [
    'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 '
    'Mobile/13B143 Safari/601.1]',
    'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/48.0.2564.23 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 5.1.1; Nexus 6 Build/LYZ28E) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/48.0.2564.23 Mobile Safari/537.36']

headers = {
    'User_Agent': random.choice(user_agents),
    'Referer': 'https://passport.weibo.cn/signin/login?entry=mweibo&res=wel&wm=3349&r=http%3A%2F%2Fm.weibo.cn%2F',
    'Origin': 'https://passport.weibo.cn',
    'Host': 'passport.weibo.cn'
}
post_data = {
    'username': '',
    'password': '',
    'savestate': '1',
    'ec': '0',
    'pagerefer': 'https://passport.weibo.cn/signin/welcome?entry=mweibo&r=http%3A%2F%2Fm.weibo.cn%2F&wm=3349&vt=4',
    'entry': 'mweibo'
}

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
    "Referer": "https://weibo.com/",

}
login_url = 'https://passport.weibo.cn/sso/login'


def login(username, password):

    post_data['username'] = username
    post_data['password'] = password
    r = session.post(login_url, data=post_data, headers=headers)
    data = json.loads(r.text)
    url1 = data['data']['crossdomainlist']['weibo.com']
    url2 = data['data']['crossdomainlist']['sina.com.cn']
    url3 = data['data']['crossdomainlist']['weibo.cn']
    uuid = data['data']['uid']
    session.get(url1)
    session.get(url2)
    session.get(url3)
    url = 'https://weibo.com/u/{}/home'.format(uuid)

    session.get(url,headers=header)
    if r.status_code != 200:
        # raise Exception('模拟登陆失败')
        logger.error('模拟登陆失败')
    else:
        logger.info("模拟登陆成功,当前登陆账号为：" + username)
#@retry()
def get_content(kname,keyword):
    page = 1
    while 1:
        news_url = 'https://s.weibo.com/list/relpage?search={}&page={}'.format(kname, page)
        try:
            response = session.get(news_url, headers=header, timeout=30)
            logger.info('requests url: {}, page: {}'.format(news_url, page))
        except:
            continue
        print response.status_code
        txt = response.text
        script = re.findall(r'<script>STK && STK.pageletM && STK.pageletM.view(.*?)</script>', txt)[2].replace('(','').replace(')','')
        data = json.loads(script)
        html = data['html']
        news_html = etree.HTML(html)
        divs = news_html.xpath('//div[@class="WB_cardwrap S_bg2 clearfix"]')
        if len(divs) == 0:
            logger.info("爬取结束")
            break
        for div in divs:
            item = {}
            try:
                news_url = div.xpath('.//p[@class="link_title2"]/a/@href')[0]
                news_title = div.xpath('.//p[@class="link_title2"]/a/@title')[0]
                news_summary = ''.join(div.xpath('.//p[@class="link_info W_textb"]//text()')).replace('\n', '').replace('\t', '').strip()
                news_source = div.xpath('.//span[@class="linkAC_from"]/text()')[0].replace('\n', '').replace('\t', '')
                news_date = div.xpath('.//span[@class="linkAC_from"]/text()')[1]
                try:
                    response = session.get(news_url, headers=header, timeout=30)
                except:
                    continue
                response.coding = 'utf-8'
                txt = response.content
                readable_article = Document(txt).summary()
                html = etree.HTML(readable_article)
            except:
                continue
            context = ''.join(html.xpath('//p//text()')).replace('\n', '').replace('\t', '')
            if context in "":
                continue
            if news_source in "":
                news_source = u"新浪"

            item['url'] = news_url
            item['title'] = news_title
            item['source'] = news_source
            item['date'] = news_date
            item['summary'] = news_summary.replace('\n','').replace('\t','')
            item['content'] = context
            item['keyword'] = keyword


            with open('./sina_news.json', 'a') as f:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        print u"第{}页爬取完成!".format(page)
        page += 1
        time.sleep(2)

def main():
    login(sina_username,sina_password)
    for keyword in search_list:
        kname = quote(keyword)
        get_content(kname,keyword)


if __name__ == '__main__':

    main()