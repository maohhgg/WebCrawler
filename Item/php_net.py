#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os

import re

import sys
from lxml import etree
from Class.WCHttp import WCHttp


class PHP:
    content = None
    tree = None
    detail = {}
    refentry = None

    def get(self, url, header=None):
        http = WCHttp()
        if header:
            http.header(header)
        http.get(url)
        self.content = http.content()
        self.url = http.get_url_detail()
        if self.content:
            self.tree = etree.HTML(self.content)
        return self

    def get_type(self):
        self.detail['url'] = str(os.path.basename(self.url.path))
        detail = self.detail['url'].split('.')
        self.detail['html_id'] = '.'.join(detail[:2])
        self.detail['type'] = detail[0]
        self.detail['url_name'] = detail[1]
        return self

    def get_mian_dom(self):
        self.get_type()
        if self.tree is not None:
            expr = '//div[@id=$name]'
            self.refentry = self.tree.xpath(expr, name=self.detail['html_id'])[0]
        return self

    def get_keys(self):
        keys = None
        if self.refentry is not None:
            keys = []
            refsect1 = self.refentry.xpath('div[contains(@class, "refsect1")]/@class')
            for e in refsect1:
                keys.append(str(e).replace('refsect1 ', ''))
        return keys

    def get_all(self):
        self.get_mian_dom()
        keys = self.get_keys()
        # for key in keys:
        self.parameters()
        self.description()
        self.returnvalues()

        print(self.detail)

    def parameters(self):
        key = sys._getframe().f_code.co_name
        param = {}
        id = 'refsect1-%s-%s' % (self.detail['html_id'], key)
        dom = self.get_dom(id=id)[0]
        dl = self.get_dom(tag='dl', target=dom)[0]
        dt = self.get_dom(tag='dt', target=dl)
        dd = self.get_dom(tag='dd', target=dl)
        for i in range(len(dd)):
            param[self.get_code(dt[i], parent=dl)] = self.get_code(dd[i], parent=dl, active=True)
        self.detail[key] = param

    def description(self):
        key = sys._getframe().f_code.co_name
        param = {'code': '', 'description': ''}
        id = 'refsect1-%s-%s' % (self.detail['html_id'], key)
        dom = self.get_dom(id=id)[0]

        methods = self.get_dom(className='dc-description', target=dom)
        para = self.get_dom(className='rdfs-comment', target=dom)

        for child in methods:
            param['code'] += self.get_code(child)
        for child in para:
            param['description'] += self.get_code(child, active=True)
        self.detail[key] = param

    def returnvalues(self):
        key = sys._getframe().f_code.co_name
        param = {'description': ''}
        id = 'refsect1-%s-%s' % (self.detail['html_id'], key)
        dom = self.get_dom(id=id)[0]
        para = self.get_dom(className='para', target=dom)
        div = self.get_dom(tag='div', target=dom)
        for e in para:
            param['description'] += '\n' + self.get_code(e, parent=dom, active=True)
        for d in div:
            param[d.get('class')] = str(self.get_code(d, parent=dom, active=True))
        self.detail[key] = param

    def get_dom(self, tag='*', className=None, id=None, target=None):
        if target is None:
            if self.tree is None:
                self.get_mian_dom()
            target = self.refentry
        if id:
            expr = '%s[@id="%s"]' % (tag, id)
        elif className:
            expr = '%s[contains(@class,"%s")]' % (tag, className)
        else:
            expr = '%s' % tag

        dom = target.xpath(expr)
        return dom

    def get_code(self, node, parent=None, active=False):
        c = ''
        if parent is None:
            parent = node.getparent()

        p = parent
        if isinstance(node, etree._ElementUnicodeResult):
            c = str(node).replace('\n', '').replace(' ', '').strip()
            if c is not '':
                mark = self.get_code_type(node, p)
                if active:
                    c = " %s " % (mark[::-1] + c + mark)
                else:
                    c += ' '
            return c

        if isinstance(node, etree._Element):
            for item in node.xpath('node()'):
                c += str(self.get_code(item, parent=node, active=active))
            if active:
                if node.tag == 'a':
                    c = " [%s](%s) " % (c, node.get('href'))
                elif node.tag == 'blockquote':
                    c = '\n>%s' % c
            return c

    def get_code_type(self, node, parent):
        type = {'code': '`', 'strong': '**', 'em': '*'}
        s = ''
        for i in range(2):
            tag = parent.tag
            if tag in type.keys():
                s += type[tag]
            else:
                s += ''
            parent = parent.getparent()
        return s
