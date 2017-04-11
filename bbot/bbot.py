from twins import Twins
from pyquery import PyQuery as pq
from time import sleep
from random import random
from re import search
from twitter import Api
from collections import defaultdict


class BBot(Twins):

    def __init__(self, username, password, path_to_is_duplicate_list,
                 consumer_key, consumer_secret,
                 access_token, access_token_secret):
        super(BBot, self).__init__(username, password)
        self.api = Api(consumer_key=consumer_key,
                       consumer_secret=consumer_secret,
                       access_token_key=access_token,
                       access_token_secret=access_token_secret)

        is_duplicate = defaultdict(lambda: False)
        with open(path_to_is_duplicate_list) as fp:
            for line in fp:
                is_duplicate[line.rstrip()] = True
        self.is_duplicate = is_duplicate

    def post_tweet(self, notification_id, text):
        if not self.is_duplicate[notification_id]:
            try:
                self.api.PostUpdate(text)
                self.update_is_duplicate(notification_id)

            except Exception as e:
                print(e)

    def update_is_duplicate(self, notification_id):
        self.is_duplicate[notification_id] = True

    def save_is_duplicate(self):
        with open('is_duplicate.list', 'w') as fp:
            for idx in self.is_duplicate.keys():
                print(idx, file=fp)

    def get_course_notifications(self):

        target_list = ['学群授業', '大学院授業']

        def is_target(d):
            """
            科目情報に関するリンクかどうかを判定
            """
            result = map(lambda t: d.text.startswith(t), target_list)
            return any(result)

        def get_attrib(d):
            """
            URLからパラメータを抜き出す
            """
            _raw = d.attrib['href'].split('?')[1]
            return _raw.split('&')

        def to_dict(attrib_list):
            """
            パラメータのリストをDictionaryに変換
            """
            return dict(map(lambda attr: attr.split('='), attrib_list))

        r = self.req("KJW0001100-flow")
        for d in pq(r.text)("a"):

            if d.text is None:
                continue

            if is_target(d):
                attrib_list = get_attrib(d)
                attrib_dict = to_dict(attrib_list)

                self.req("KJW0001100-flow")
                rr = self.get(attrib_dict)
                for dd in pq(rr.text)("a"):
                    title = dd.text

                    dd_attrib_list = get_attrib(dd)
                    dd_attrib_dict = to_dict(dd_attrib_list)

                    if not search(r'休講|変更', title):
                        continue

                    if dd_attrib_dict['_eventId'] == 'confirm':
                        self.req("KJW0001100-flow")
                        self.get(attrib_dict)
                        rrr = self.get(dd_attrib_dict)

                        body = pq(rrr.text)("div.keiji-naiyo")

                        if not title or not body:
                            continue

                        tweet = title + '\n' + body.text()
                        tweet = tweet[:140]

                        notification_id = dd_attrib_dict['seqNo']
                        self.post_tweet(notification_id, tweet)

                        span = random() * 5
                        sleep(span)

            self.save_is_duplicate()
