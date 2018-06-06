#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-11-27 12:20:11
# @Author  : guangqiang_xu (981886190@qq.com)
# @Link    : http://www.treenewbee.com/
# @Version : $Id$
import os
import time
import logging
import sys
import shutil

#log_folder_name = '%s_logs' % spider_name

def spider_log(log_name, log_folder_name, level=logging.INFO,delete_existed_log=True):
 
    file_folder = log_folder_name
    if os.path.exists(file_folder):
        if delete_existed_log:
            shutil.rmtree(file_folder)
            os.mkdir(file_folder)
    else:
        os.mkdir(file_folder)

    create_time = time.strftime('%Y-%m-%d %H-%M-%S')
    # 创建一个logger
    logger = logging.getLogger(log_name)
    # 设置日志级别

    logger.setLevel(level)

    # 创建文件处理器
    file_handler = logging.FileHandler('%s/%s_%s.txt' % (file_folder, log_name, create_time))
    file_handler.setLevel(logging.INFO)
    # 创建输出处理器
    stream_handler = logging.StreamHandler()

    # 定义输出格式
    formatter = logging.Formatter('[%(asctime)s] - %(filename)s - [line:%(lineno)d] - [%(levelname)s]: %(message)s')
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    # 给logger添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger

# 单例模式
#logger = spider_log(log_name=spider_name)


if __name__ == '__main__':
    logger = spider_log('log')
    logger.warning('warn message')
    logger.info('info message')
    logger.debug('debug message')