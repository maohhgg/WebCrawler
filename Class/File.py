#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import time


class File:
    @classmethod
    def get(cls, dir, file):
        return {
            'name': file,
            'type': file[file.find('.'):len(file)],
            'size': cls.get_file_size(dir + file),
            'ctime': cls.get_file_ctime(dir + file),
            'utime': cls.get_file_utime(dir + file)
        }

    @classmethod
    def unix_to_date(cls, timestamp):
        timeStruct = time.localtime(timestamp)
        return time.strftime('%Y-%m-%d %H:%M:%S', timeStruct)

    @classmethod
    def get_file_size(cls, file):
        step = ['B','KB', 'MB', 'GB', 'TB', 'PB']
        fsize = os.path.getsize(file)
        i = 0
        while fsize > 1024:
            fsize /= 1024
            i += 1
        return str(int(fsize)) + step[i]

    @classmethod
    def get_file_ctime(cls, file):
        t = os.path.getctime(file)
        return cls.unix_to_date(t)

    @classmethod
    def get_file_utime(cls, file):
        t = os.path.getmtime(file)
        return cls.unix_to_date(t)
