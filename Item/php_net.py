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
    detail = {'data': {}}
    refentry = None
    note = ['caution', 'warning', 'methodsynopsis dc-description']

    def __init__(self):
        self.http = WCHttp()

    def __getattr__(self, name):
        if name.find('class_') > -1:
            pass
        elif name.find('return') > -1:
            self.description(name)
        return None

    def get(self, url, header=None):
        if header:
            self.http.header(header)
        self.http.get(url)
        self.content = self.http.content()
        self.url = self.http.get_url_detail()
        if self.content:
            self.tree = etree.HTML(self.content)
        return self

    def get_type(self):
        """
        得到基本的信息
        :return:
        """
        url = str(os.path.basename(self.url.path))
        self.detail['url'] = url
        detail = url.split('.')
        self.detail['html_id'] = '.'.join(detail[:2])  # 取到想要内容的 id
        self.detail['data']['type'] = detail[0]  # 判定类型 function class ...
        self.detail['data']['path'] = self.detail['html_id']
        return self

    def get_mian_dom(self):
        """
        得到全局的有效节点，
        :return:
        """
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
        self.detail['data'] = {}
        self.get_type()
        self.get_mian_dom()
        keys = self.get_keys()
        if self.detail['data']['type'] == 'class':
            self.class_name()
            self.get_class()
        else:
            self.real_name()
            for key in keys:
                func = getattr(self, key)
                if func:
                    func()
        return self.detail['data']

    def class_name(self):
        self.detail['data']['refname'] = self.get_code(self.get_dom(tag='h1', className='title')[0])
        self.detail['data']['verinfo'] = self.get_code(self.get_dom(tag='div/p', className='verinfo')[0])
        pass

    def get_class(self):
        key = ['intro', 'synopsis', 'constants', 'props']
        section = self.get_dom(tag='div/div', className='section')
        for i in range(len(section)):
            func = getattr(self, ('class_%s' % key[i]))
            func(section[i])
        pass

    def class_intro(self, dom):
        """
        方法 简介
        function examples
        :return: null
        """
        key = str(sys._getframe().f_code.co_name).replace('class_', '')
        param = {'description': ''}
        p = self.get_dom(tag='p', className='para', parent=dom)
        for e in p:
            param['description'] += self.get_code(e, parent=dom)
        self.detail['data'][key] = param

    def class_synopsis(self, dom):
        """
        类 类摘要
        function examples
        :return: null
        """
        key = str(sys._getframe().f_code.co_name).replace('class_', '')
        code = self.get_dom(tag='div', className='classsynopsis', parent=dom)[0]
        codes = "```php"
        for strings in code:
            cls = strings.get('class')
            if cls != 'classsynopsisinfo':
                codes += "    "

            if cls in self.note:
                codes += (self.get_code(strings, parent=code, mark=['span']))['code'].strip()
            else:
                codes += self.get_code(strings, parent=code, mark=['span']).strip()

            if cls:
                codes += "\n"

        self.detail['data'][key] = codes + '}\n```'

    def class_constants(self, dom):
        """
        方法 预定义常量
        function examples
        :return: null
        """
        key = str(sys._getframe().f_code.co_name).replace('class_', '')
        param = []
        dl = self.get_dom(tag='dl', parent=dom)
        if dl:
            dl = dl[0]
            dt = self.get_dom(tag='dt', parent=dl)
            dd = self.get_dom(tag='dd', parent=dl)

            for i in range(len(dd)):
                param.append([self.get_code(dt[i], parent=dl), self.get_code(dd[i], parent=dl)])
            self.detail['data'][key] = param

    def class_props(self, dom):
        """
        方法 属性
        function examples
        :return: null
        """
        key = str(sys._getframe().f_code.co_name).replace('class_', '')
        param = []
        dl = self.get_dom(tag='dl', parent=dom)
        if dl:
            dl = dl[0]
            dt = self.get_dom(tag='dt', parent=dl)
            dd = self.get_dom(tag='dd', parent=dl)

            for i in range(len(dd)):
                param.append([self.get_code(dt[i], parent=dl), self.get_code(dd[i], parent=dl)])
            self.detail['data'][key] = param

    def real_name(self):
        dom = self.get_dom(tag='div', className='refnamediv')[0]
        refname = self.get_dom(tag='h1', parent=dom)
        name = []
        if len(refname) > 1:
            for e in refname:
                name.append(self.get_code(e, parent=dom))
        elif len(refname) == 1:
            name = self.get_code(refname[0], parent=dom)
        self.detail['data']['refname'] = name
        self.detail['data']['verinfo'] = self.get_code(self.get_dom(tag='p', className='verinfo', parent=dom)[0],
                                                       parent=dom)
        self.detail['data']['purpose'] = self.get_code(self.get_dom(tag='p', className='refpurpose', parent=dom)[0],
                                                       parent=dom)

    def parameters(self):
        """
        方法 参数
        function parameters
        :return: null
        """
        key = sys._getframe().f_code.co_name
        param = []
        id = 'refsect1-%s-%s' % (self.detail['html_id'], key)
        dom = self.get_dom(id=id)[0]
        dl = self.get_dom(tag='dl', parent=dom)
        if dl:
            dl = dl[0]
            dt = self.get_dom(tag='dt', parent=dl)
            dd = self.get_dom(tag='dd', parent=dl)
            for i in range(len(dd)):
                detail = {'title': self.get_code(dt[i], parent=dl, active=False), 'description': ''}
                string = ''
                for d in dd[i].getchildren():
                    if d.tag == 'dl':
                        ddt = self.get_dom(tag='dt', parent=d)
                        ddd = self.get_dom(tag='dd', parent=d)
                        for j in range(len(ddd)):
                            string += self.get_code(ddt[j], parent=d) + '\n'
                            string += "   %s\n" % self.get_code(ddd[j], parent=d)
                    elif d.get('class') not in self.note:
                        string += self.get_code(d, parent=dd[i]) + '\n'
                    else:
                        data = self.get_code(d, parent=dd[i], mark=['span'])
                        if 'code' in data.keys():
                            data['code'] = "```php\n%s\n```" % data['code']
                        detail.update(data)  # self.note中的是返回 dict
                detail['description'] = string
                param.append(detail)
        else:
            param = self.get_code(dom)
        self.detail['data'][key] = param

    def description(self, name=None):
        """
        方法 说明
        function description
        :return: null
        """
        if name:
            key = name
            mark = 'docs'
        else:
            key = sys._getframe().f_code.co_name
            mark = key
        param = {'description': ''}
        id = 'refsect1-%s-%s' % (self.detail['html_id'], key)
        dom = self.get_dom(id=id)[0]
        for d in dom.getchildren():
            if d.get('class') in self.note:
                data = self.get_code(d, parent=dom, mark=['span'])
                if 'code' in data.keys():
                    data['code'] = "```php\n%s\n```" % data['code']
                param.update(data)
            elif d.tag != 'h3':
                param['description'] += self.get_code(d, parent=dom) + '\n\n'
        self.detail['data'][mark] = param

    def returnvalues(self):
        """
        方法 返回值
        function returnvalues
        :return: null
        """
        key = sys._getframe().f_code.co_name
        param = {'description': ''}
        id = 'refsect1-%s-%s' % (self.detail['html_id'], key)
        dom = self.get_dom(id=id)[0]
        para = self.get_dom(className='para', parent=dom)
        div = self.get_dom(tag='div', parent=dom)
        for e in para:
            param['description'] += self.get_code(e, parent=dom) + '\n'
        for d in div:
            param[d.get('class')] = str(self.get_code(d, parent=dom))
        self.detail['data'][key] = param

    def changelog(self):
        """
        方法 更新日志
        function changelog
        :return: null
        """
        key = sys._getframe().f_code.co_name
        param = []
        id = 'refsect1-%s-%s' % (self.detail['html_id'], key)
        dom = self.get_dom(id=id)[0]
        tbody = self.get_dom(tag='table/tbody', parent=dom)[0]
        tr = self.get_dom(tag='tr', parent=tbody)
        for td in tr:
            param.append(str(self.get_code(td, parent=dom)))
        temp = []
        for p in param:
            log = p.strip('\n').strip('|').split('|')
            temp.append({'version': log[0], 'detail': log[1], })
        self.detail['data'][key] = temp

    def examples(self):
        """
        方法 范例
        function examples
        :return: null
        """
        key = sys._getframe().f_code.co_name
        param = []
        id = 'refsect1-%s-%s' % (self.detail['html_id'], key)
        dom = self.get_dom(id=id)[0]
        for e in dom.xpath('node()'):
            if isinstance(e, etree._ElementUnicodeResult):
                c = str(e).replace('\n', '').replace("   ", "").strip()
                if c:
                    param.append(c)
            elif e.get('class') == 'example':
                temp_id = e.get('id')
                temp = {}
                temp.update({'id': temp_id})  # id examples-5758 类似东西
                temp.update({'title': str(self.get_code(self.get_dom(tag='p/strong', parent=e)[0]))
                            .replace("  ", ' ').replace("  ", " ")})
                content = self.get_dom(className='example-contents', parent=e)
                contentString = ''
                for c in content:
                    active = ('phpcode' not in [cc.get('class') for cc in c])
                    contentString += self.get_code(c, parent=content, active=active) + '\n'
                temp.update({'description': contentString})
                param.append(temp)
            elif e.tag != 'h3':
                c = self.get_code(e, parent=dom)
                if c:
                    param.append(c)
        self.detail['data'][key] = param

    def seealso(self):
        """
        方法 参见
        function seealso
        :return: null
        """
        key = sys._getframe().f_code.co_name
        param = []
        id = 'refsect1-%s-%s' % (self.detail['html_id'], key)
        dom = self.get_dom(id=id)[0]
        ul = self.get_dom(tag='ul/li', parent=dom)
        for li in ul:
            param.append(self.get_code(li))
        if len(param) > 0:
            self.detail['data'][key] = ''.join(param)

    def errors(self):
        """
        方法 错误／异常
        function errors
        :return: null
        """
        key = sys._getframe().f_code.co_name
        param = []
        id = 'refsect1-%s-%s' % (self.detail['html_id'], key)
        dom = self.get_dom(id=id)[0]
        para = self.get_dom(className='para', parent=dom)
        for p in para:
            param.append(self.get_code(p))
        self.detail['data'][key] = param

    def notes(self):
        """
        方法 注释
        function notes
        :return: null
        """
        key = sys._getframe().f_code.co_name
        param = []
        id = 'refsect1-%s-%s' % (self.detail['html_id'], key)
        dom = self.get_dom(id=id)[0]
        notes = self.get_dom(tag='blockquote', parent=dom)
        notes += self.get_dom(tag='div', parent=dom)
        notes += self.get_dom(tag='p', className='para', parent=dom)

        for note in notes:
            if note.tag == 'blockquote':
                blockContent = []
                blockString = ''
                for block in note.getchildren():
                    if block.get('class') in self.note:
                        if blockString != '':
                            blockContent.append(blockString)
                            blockString = ''
                            blockContent.append(self.get_code(block, parent=note))
                    else:
                        blockString += self.get_code(block, parent=note) + '\n'
                if blockString != '':
                    blockContent.append(blockString)
                param.append({'note': blockContent})
            elif note.get('class') == 'para':
                text = self.get_code(note)
                param.append(text)
            else:
                text = self.get_code(note)
                param.append(text)
        self.detail['data'][key] = param

    def get_dom(self, tag='*', className=None, id=None, parent=None):
        """
        根据xpath返回节点
        :param tag:  标签名 a => <a></a>    a/b => <a><b></b></a>
        :param className:   class names
        :param id:          id name
        :param parent:      父节点
        :return:
        """
        # 如果父节点为空 使用 self.refentry
        if parent is None:
            if self.tree is None:
                self.get_mian_dom()
            parent = self.refentry
        if id:
            expr = '%s[@id="%s"]' % (tag, id)
        elif className:
            expr = '%s[contains(@class,"%s")]' % (tag, className)
        else:
            expr = '%s' % tag

        dom = parent.xpath(expr)
        return dom

    def get_code(self, node, parent=None, active=True, mark=None, except_tag=''):
        c = ''
        if parent is None:
            parent = node.getparent()
        p = parent

        # 内容为文本
        if isinstance(node, etree._ElementUnicodeResult):
            if parent.tag == 'span' and parent.get('style'):
                c = str(node)
            else:
                c = str(node).replace('\n', '').replace("   ", "").strip()
            m = self.get_code_type(p, mark)
            # 将文本保存为markdown
            if c is not '' and active and m:
                c = m[::-1] + c + m
            return c

        # 内容为节点
        if isinstance(node, etree._Element):
            if node.tag == except_tag:
                return
            elif node.tag == 'pre':
                return '\n```\n%s\n```\n' % node.text
            elif node.tag == 'br':
                return '\n'

            for item in node.xpath('node()'):
                c += str(self.get_code(item, parent=node, active=active, mark=mark, except_tag=except_tag))

            # 将文本保存为markdown
            if active:
                # 当为a标签时，手动指定mark，需要判断
                if (node.tag == 'a') and (mark is None or 'a' in mark):
                    c = " [%s](%s) " % (c, node.get('href'))
                elif node.tag == 'blockquote':
                    c = '\n > %s' % c
                elif node.tag == 'table':
                    c = "\n%s" % c
                elif node.tag == 'thead':
                    d = c.strip('\n').strip('|').split('|')
                    s = '|'
                    for i in d:
                        s += ':---|'
                    c = '\n\n %s %s \n' % (c, s)
                elif node.tag == 'tr':
                    c = '%s |\n' % c
                elif node.tag == 'td' or node.tag == 'th':
                    c = '| %s' % c
                elif node.tag == 'li':
                    c = '* %s\n' % c

            # 代码段
            if node.get('class') == 'phpcode':
                c = '\n```php\n%s\n```\n' % c.strip().strip('` \n `')
            # 当内容为警告提示框或函数用法提示框
            elif (node.get('class') in self.note) and node.tag == 'div':
                # 函数用法提示框 key 改为 'code'
                if node.get('class') == 'methodsynopsis dc-description':
                    c = {'code': c.replace("  ", " ").replace("  ", " ")}
                else:
                    c = {node.get('class'): c}
            return c

    def get_code_type(self, node, mark):
        """
        根据标签返回markdown的符号
        :param node: 要被识别的节点标签
        :return:  字符s
        """
        keys = {'code': '` ', 'strong': '** ', 'em': '* ', 'span': ' '}
        if mark is None:
            mark = list(keys.keys())
        s = ''
        for i in range(2):
            tag = node.tag
            if tag in mark:
                s += keys[tag]
            else:
                s += ''
            node = node.getparent()
        return s
