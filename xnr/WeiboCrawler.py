import time

from selenium import webdriver

from SinaLauncher import SinaLauncher

class WeiboCrawler(object):
    def __init__(self):
        self.driver = webdriver.Firefox()

    def get_present_time(self):
        present_time_stamp = time.localtime(int(time.time()))
        present_time = time.strftime("%Y-%m-%d %H:%M:%S", present_time_stamp)
        year = int(present_time.split(" ")[0].split("-")[0])
        month = int(present_time.split(" ")[0].split("-")[1])
        day = int(present_time.split(" ")[0].split("-")[2])
        hour = int(present_time.split(" ")[1].split(":")[0])
        minute = int(present_time.split(" ")[1].split(":")[1])
        second = int(present_time.split(" ")[1].split(":")[2])
        return year, month, day, hour, minute, second

    def all_weibo_xnr_crawler(self):
        query_body = {
            'query': {'term': {'create_status': 2}},
            'size': 10000
        }
        search_results = es.search(index=weibo_xnr_index_name, doc_type=weibo_xnr_index_type, body=query_body)['hits']['hits']
        if search_results:
            for result in search_results:
                result = result['_source']
                mail_account = result['weibo_mail_account']
                phone_account = result['weibo_phone_account']
                pwd = result['password']
                if mail_account:
                    account_name = mail_account
                elif phone_account:
                    account_name = phone_account
                else:
                    account_name = False
                    if account_name:
                        self.execute(account_name, pwd)

    def execute(self, uname, upasswd):
        xnr = SinaLauncher(uname, upasswd)
        print xnr.login()
        print 'uname::', uname
        uid = xnr.uid
        current_ts = int(time.time())

        timestamp_retweet, timestamp_like, timestamp_at, timestamp_private, \
        timestamp_comment_receive, timestamp_comment_make = self.newest_time_func(xnr.uid)

        print timestamp_retweet, timestamp_like, timestamp_at, \
            timestamp_private, timestamp_comment_receive, timestamp_comment_make

        # try:
        print 'start run weibo_feedback_follow.py ...'
        fans, follow, groups = self.FeedbackFollow(xnr.uid, current_ts).execute()
        print 'run weibo_feedback_follow.py done!'
        # except:
        #     print 'Except Abort'

        # try:
        print 'start run weibo_feedback_at.py ...'
        self.FeedbackAt(xnr.uid, current_ts, fans, follow, groups, timestamp_at).execute()
        print 'run weibo_feedback_at.py done!'


        print 'start run weibo_feedback_comment.py ...'
        self.FeedbackComment(xnr.uid, current_ts, fans, follow, groups, timestamp_comment_make,
                        timestamp_comment_receive).execute()
        print 'run weibo_feedback_comment.py done!'

        print 'start run weibo_feedback_like.py ...'
        self.FeedbackLike(xnr.uid, current_ts, fans, follow, groups, timestamp_like).execute()
        print 'run weibo_feedback_like.py done!'


        print 'start run weibo_feedback_private.py ...'
        # print 'timestamp_private:::',timestamp_private
        # print 'current_ts::::::',current_ts
        self.FeedbackPrivate(xnr.uid, current_ts, fans, follow, groups, timestamp_private).execute()
        print 'run weibo_feedback_private.py done!'


        print 'start run weibo_feedback_retweet.py ...'
        self.FeedbackRetweet(xnr.uid, current_ts, fans, follow, groups, timestamp_retweet).execute()
        print 'run weibo_feedback_retweet.py done!'


