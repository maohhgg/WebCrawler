#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os

import requests

from Class.File import File


class WCFile:
    NOT_DIR = '目录不存在'
    NOT_FILE = '文件不存在'
    DOWNLOAD_MAX_SIZE = 10 * 1024 * 1024  # 最大下载文件大小 MB
    DOWNLOAD_SPLIT_SIZE = 1024  # 下载分段大小 KB

    TYPE_FILE = 'local'
    TYPE_HTTP = 'http'
    TYPE_HTTPS = 'https'
    TYPE_SMB = 'smb'

    def __init__(self):
        self._dir = './'
        self._type = None
        self._uri = None
        self._file = None

    def get_name(self):
        return self._file_name

    def set_dir(self, dir):
        if os.path.isdir(dir):
            self._dir = dir
            return self
        else:
            self._error(self.NOT_DIR)
        return self

    def uri(self, string):
        index = string.find('://')
        if index > 0:
            self._type = string[0:index]
            self._file_name = string[self._get_url_file_dir(string, '/') + 1:len(string)]
            # self._dir = string[0:self._get_url_file_dir(string, '/') + 1]
        elif os.path.isfile(string) or os.path.isfile(self._dir + string):
            self._type = self.TYPE_FILE
            if '/' in string:
                self._dir = string[0:self._get_url_file_dir(string, '/') + 1]
                self._file_name = string[self._get_url_file_dir(string, '/') + 1:len(string)]
            else:
                self._file_name = string
            self._file = File.get(self._dir, self._file_name)
        else:
            self._error(self.NOT_FILE)
        self._uri = string
        return self

    def _info(self, c):
        print("\033[32mINFO: \033[0m" + c)

    def _error(self, c):
        print("\033[0;31mERROR: \033[0m" + c)

    def _get_url_file_dir(self, string, char):
        last_position = -1
        while True:
            position = string.find(char, last_position + 1)
            if position == -1:
                return last_position
            last_position = position

    def _valid(self):
        if self._file_name and self._type and self._dir:
            return True
        else:
            return False

    def download(self, id=None):
        if self._valid() and (self._type != self.TYPE_FILE):

            # r = requests.get(self._uri, stream=True)
            r = requests.get(self._uri)

            if r.status_code == 200:
                # self._info('已获取:' + self._file_name)
                size = int(r.headers['content-length'])
                if size and size > self.DOWNLOAD_MAX_SIZE:
                    self._info(self._uri + '\n这个文件太大，有可能下载失败，最好使用其他方式下载')

                # with open('test', 'wb') as fd:
                #     for chunk in r.iter_content(1024 * 100):
                #         fd.write(chunk)
                self._save(r.content, 'wb')
                if os.path.isfile(self._dir + self._file_name):
                    self._info(str(id) + ' - ' + self._file_name + '下载完成!')
                    return self._file_name
                else:
                    self._error(self._uri + '下载失败!')
                    return False
            else:
                self._error(self._uri + 'Response Code' + str(r.status_code))
                return self._uri
        return self

    def _save(self, content=None, access_mode='a+', name=None):
        if content and self._valid():
            file = open(self._dir + self._file_name, access_mode)
            file.write(content)
            file.close()
            self._file = File.get(self._dir, self._file_name)
        else:
            self._info('文件已重建')
        return self

        # def get_file_content(self, file_name=None):
        #
        # def read_line(self, line=None, file_name=None):
        #
        # def wirte_line(self, content, line=None, file_name=None):
        #


        # def open(self,file_name=None):
        #     return self
        #
        # def get_file_name(self):
        #     return self._file.name

# 调试内容

# def prn_obj(obj):
#     print('\n'.join(['%s:%s' % item for item in obj.__dict__.items()]))
#
#
# def main():
#     url = 'https://img3.doubanio.com/view/movie_poster_cover/lpst/public/p930569361.jpg'
#     # url = 'https://goodday.ddns.net/omega.bak'
#     mcf = WCFile()
#     mcf.uri(url)
#     mcf.set_dir('./public/image/').download()
#     prn_obj(mcf)
#
#
# if __name__ == '__main__':
#     main()
