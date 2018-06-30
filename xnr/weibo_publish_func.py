#-*- coding:utf-8 -*-
import os
import time
import json
import sys
import urllib
import urllib2


from weibo_publish import weibo_publish_main
from weibo_operate import SinaOperateAPI
from SinaLauncher import SinaLauncher
from global_utils import es_xnr as es
from global_utils import weibo_feedback_comment_index_name_pre,weibo_feedback_comment_index_type,\
                        weibo_feedback_retweet_index_name_pre,weibo_feedback_retweet_index_type,\
                        weibo_feedback_private_index_name_pre,weibo_feedback_private_index_type,\
                        weibo_feedback_at_index_name_pre,weibo_feedback_at_index_type,\
                        weibo_feedback_like_index_name_pre,weibo_feedback_like_index_type,\
                        weibo_feedback_fans_index_name,weibo_feedback_fans_index_type,\
                        weibo_feedback_follow_index_name,weibo_feedback_follow_index_type,\
                        weibo_xnr_index_name,weibo_xnr_index_type,weibo_report_management_index_name_pre,\
                        weibo_report_management_index_type,weibo_xnr_fans_followers_index_name,\
                        weibo_xnr_fans_followers_index_type,weibo_hot_keyword_task_index_name,\
                        weibo_hot_keyword_task_index_type,index_sensing,type_sensing,\
                        xnr_flow_text_index_name_pre,xnr_flow_text_index_type
from utils import save_to_fans_follow_ES,xnr_user_no2uid
from weibo_xnr_flow_text_mappings import weibo_xnr_flow_text_mappings
from time_utils import ts2datetime