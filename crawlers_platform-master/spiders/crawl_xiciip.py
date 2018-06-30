#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-11-27 12:20:11
# @Author  : guangqiang_xu (981886190@qq.com)
# @Link    : http://www.treenewbee.com/
# @Version : $Id$
import time
import requests
import pymysql
from scrapy.selector import Selector

conn = pymysql.connect(host='localhost',user='root',passwd='',db='proxy',port=3306,charset='utf8')
cursor = conn.cursor()

#爬取西刺代理的免费代理
def crawl_ips():
    headers = {"User-Agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
    for i in range(1000):
        print("正在爬取{0}页.".format(i))
        time.sleep(2)
        res = requests.get("http://www.xicidaili.com/nn/{0}".format(i),headers=headers)
        selector = Selector(text=res.text)
        all_trs = selector.css("#ip_list tr")

        ip_list = []
        for tr in all_trs[1:]:
            speed_str = tr.css(".bar::attr(title)").extract()[0]
            if speed_str:
                speed = float(speed_str.split(u"秒")[0])
            all_texts = tr.css("td::text").extract()
            ip = all_texts[0]
            print "ip**ip**ip"
            port = all_texts[1]
            xici_type = all_texts[5]
            ip_list.append((ip,port,speed,xici_type))

        for ip_info in ip_list:
            print("{0}>>正在存储到MySql数据库中".format(ip_info))
            cursor.execute(
                "insert into xici(ip,port,speed,type) VALUES ('{0}','{1}',{2},'{3}')".format(ip_info[0],ip_info[1],ip_info[2],ip_info[3])
            )
            conn.commit()

# crawl_ips()


class GetIP(object):

    def delete_ip(self,ip):
        #从数据库中删除无效的ip
        delete_sql = """
            delete from xici where ip="{0}"
        """.format(ip)
        cursor.execute(delete_sql)
        conn.commit()
        return True


    #判断ip是否可用
    def judeg_ip(self,ip,port,type,speed):
        http_url = 'http://www.baidu.com'
        proxy_type = type.lower()
        proxy_url = '{0}://{1}:{2}'.format(proxy_type,ip,port)

        try:
            proxy_dict = {
                proxy_type:proxy_url
            }
            print proxy_dict
            response = requests.get(http_url,proxies=proxy_dict,timeout=5)
        except Exception as e:
            print("invaild ip and port")
            self.delete_ip(ip)
            return False
        else:
            code = response.status_code
            if code>=200 and code<300:
                print("effctive ip")
                return True
            else:
                print("invaild ip and port")
                self.delete_ip(ip)

    #从数据库中随机获取一个ip
    def get_random_ip(self):
        random_sql = """SELECT ip,port,speed,type FROM xici
                  ORDER BY RAND()
                  LIMIT 1
                  """
        result = cursor.execute(random_sql)
        for ip_info in cursor.fetchall():
            ip = ip_info[0]
            # print "ip+++ip+++ip", type(ip)
            port = ip_info[1]
            # print "port+++port+++port", type(port)
            speed = ip_info[2]
            # print "speed+++speed+++speed", type(speed)
            type = ip_info[3]
            # print "type+++type+++type", type(xici_type)
            result = self.judeg_ip(ip,port,type,speed)
            if result:
                proxy_type = type.lower()
                return {"{}".format(proxy_type): "{0}://{1}:{2}".format(type,ip,port)}
            else:
                return self.get_random_ip()

get_ip = GetIP()


if __name__ == '__main__':
    # crawl_ips()
    get_ip = GetIP()
    print get_ip.get_random_ip()
    

