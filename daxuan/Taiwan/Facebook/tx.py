#!/usr/bin/env python
# -*- coding: utf-8 -*-
from time import sleep
from selenium import webdriver

driver = webdriver.PhantomJS()
driver.get("https://www.facebook.com/")
# driver.get("https://www.facebook.com/")
sleep(5)
driver.find_element_by_xpath('//table[@cellspacing="0"]/tbody/tr[2]/td[1]/input').send_keys('+8613269704912')
driver.find_element_by_xpath('//table[@cellspacing="0"]/tbody/tr[2]/td[2]/input').send_keys('chenhuiping')
driver.find_element_by_xpath('//table[@cellspacing="0"]/tbody/tr[2]/td[3]/input').click()
driver.save_screenshot("facebook.png")
driver.close()