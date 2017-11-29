#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
import requests


class WCHttp:
    def __init__(self):
        self._headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN, zh;',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
        }
        self.s = requests.Session()

    def header(self, *args):
        if len(args) < 1:
            return self
        if type(args[0]) != type('ss'):
            print(args)
            for item in args:
                print(item)
                self._headers[item[0]] = item[1]
        elif len(args) > 1:
            for i in range(0, len(args), 2):
                self._headers[args[i]] = args[i + 1]

        self.s.headers.update(self._headers)
        return self

    def get(self, url):
        self.re = self.s.get(url)
        if self.re.status_code == 200:
            self._content_type = self._get_content_type(self.re.headers['content-type'])
            if self.re.cookies:
                self.header('Cookies', self.re.cookies)
        else:
            print("---")
            # something code
        return self

    def post(self, url, data=None):
        return self

    def run(self, func):
        self._func = func
        return self

    def content(self):
        if self._content_type[1] == 'json':
            return json.loads(self.re.content)
        elif self._func:
            return self._func(self.re.content)

    def _get_content_type(self, string):
        arr = string.split(';')
        types = str(arr[0]).split('/')
        return types


# 调试内容
#
# def prn_obj(obj):
#     print('\n'.join(['%s:%s' % item for item in obj.__dict__.items()]))
#
#
# def main():
#     url = 'http://qust.me:8889/api/one/date/2013-03-07'
#     http = WCHttp()
#     http.get(url)
#     print(http.content())
#     # prn_obj(http)
#
#
# if __name__ == '__main__':
#     main()
