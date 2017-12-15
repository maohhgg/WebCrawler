#!/usr/bin/env python
# -*- coding:utf-8 -*-

from Class.WCHttp import WCHttp
from lxml import etree


class douban:
    content = None
    tree = None

    def get(self, url, header=None):
        if header is None:
            header = []
        http = WCHttp()
        http.header(header)
        http.get(url)
        self.content = http.content()
        if self.content:
            self.tree = etree.HTML(self.content)
        return self

    def get_image(self):
        if self.tree:
            img = self.tree.xpath('//div[@id="mainpic"]/a[@class="nbgnbg"]/img/@src')
            return img[0]
        else:
            return ''

    def get_description(self):
        if self.tree:
            text = self.tree.xpath('//div[@id="link-report"]/span[1]/text()')
            l = len(text)
            for line in range(0, l):
                text[line] = str(text[line]).strip()
            text = '\n\r'.join(text)
            if text == ('\n\r' * (l-1)):
                text = self.tree.xpath('//div[@id="link-report"]/span[2]/text()')
                l = len(text)
                for line in range(0, l):
                    text[line] = str(text[line]).strip()
                text = '\n\r'.join(text)
            return text
        else:
            return ''

#
# if __name__ == '__main__':
#     db = douban()
#     url = 'https://movie.douban.com/subject/1295526/'
#     cookies = ['cookies',
#                'bid=YK3_Rwx8jE4; ll="118318"; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1512345665%2C%22https%3A%2F%2Fwww.douban.com%2F%22%5D; ap=1; _pk_id.100001.4cf6=9ecfeaf49f97bab3.1511954736.7.1512347818.1512234123.; _pk_ses.100001.4cf6=*; __utma=30149280.1818481521.1511694241.1512233975.1512345665.8; __utmb=30149280.0.10.1512345665; __utmc=30149280; __utmz=30149280.1511694241.1.1.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utma=223695111.1889745337.1511954736.1512233975.1512345665.7; __utmb=223695111.0.10.1512345665; __utmc=223695111; __utmz=223695111.1512230764.5.4.utmcsr=douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; _vwo_uuid_v2=1B8F7FC4A70304978ABE8206EA0F8D4E|61ec45fb1b365fb26f2769fa67afeb48']
#     db.get(url, cookies)
#     print(db.get_description())
