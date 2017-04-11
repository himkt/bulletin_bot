from twins import Twins
from pyquery import PyQuery as pq
from time import sleep
from random import random
from re import search


class BBot(Twins):

    def __init__(self, username, password):
        super(BBot, self).__init__(username, password)

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
                        if title and body:
                            print(title, body.text())

                        span = random() * 5
                        sleep(span)


if __name__ == '__main__':
    client = BBot('<your student id>', 'password')
    client.get_course_notifications()
