# coding:utf-8
import requests
from lxml import etree
from readability.readability import Document
import time
import json
import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sess = requests.session()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"}

def get_url():
    start_url = "http://www.ediliziaeterritorio.ilsole24ore.com/"
    sess.get(start_url, headers=headers)
    page = 1
    keyword = 'Luigi Di Maio'
    url = "http://www.ricerca24.ilsole24ore.com/s24service?profilo=r24_service&search_query_id=fullquery&max_docs=1000&highlight=true&keywords_operator=AND&search_parameters=&order_by=2&page_number={}&page_size=10&v=2009&mt=text%2Fhtml%3B%20charset%3Diso-8859-1&cog_extra=true&xsl_id=html_all&keywords={}".format(page,keyword)
    response = sess.get(url, headers=headers)
    txt = response.text
    html = etree.HTML(txt)
    lis = html.xpath('//ul[@class="list list-results"]/li[@class="i"]')
    for li in lis:
        news_url = li.xpath('./article//h3/a/@href')[0]
        try:
            date = re.search(r'\d+-\d+-\d+', news_url).group()
        except:
            d = re.search(r'\d+/\d+/\d+', news_url).group()
            date = d.replace('/', '-')
        timeArray = time.strptime(date, "%Y-%m-%d")
        timestamp = int(time.mktime(timeArray))
        stringDate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
        response = sess.get(news_url, headers=headers)
        txt = response.text
        try:
            num = re.findall(r'\d+ Commenti', txt)
            print num
            num = num[0].split(' ')[0]
        except Exception as error:
            print error
            num = 0
        readable_article = Document(txt)
        title = readable_article.title()
        html = etree.HTML(readable_article.summary())
        context = ''.join(html.xpath('//p//text()')).replace('\r','').replace('\n','').replace('\t','')
        item = {}
        item['time'] = stringDate
        item['timestamp'] = timestamp
        item['title'] = title
        item['context'] = context
        item['source'] = 'ricerca24'
        item['url'] = news_url
        item['commont_num'] = num
        with open('24.json', 'a') as f:
            f.write(json.dumps(item)+'\n')

if __name__ == '__main__':
    get_url()