#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-18 11:00:02
# @Author  : guangqiang_xu (981886190@qq.com)
# @Version : $Id$
#from __future__ import unicode_literals
from pytrends.request import TrendReq

def down_data(keyword, date, geo):
	pytrends = TrendReq(hl='en-US', tz=360)
	kw_list = [str(keyword)]
	pytrends.build_payload(kw_list, cat=0, timeframe=date, geo=geo, gprop='')
	response = pytrends.interest_over_time()
	response.to_csv(keyword +'.csv', sep=',', header=True, index=True)
if __name__ == '__main__':
	# 参数 人名，时间段，国家代码
	down_data("Влади́мир Влади́мирович Пу́тин", '2017-10-1 2018-3-8', 'RU')
