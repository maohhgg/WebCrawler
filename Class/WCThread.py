#!/usr/bin/env python
# -*- coding:utf-8 -*-
import threading

class WCThread(threading.Thread):
    """
    doc of class
    Attributess:
        func: 线程函数逻辑
    """
    def __init__(self, func):
        super(WCThread, self).__init__()  # 调用父类的构造函数
        self.func = func  # 传入线程函数逻辑

    def run(self):
        # do something
        self.func()