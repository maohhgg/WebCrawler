#!/usr/bin/env python
# -*- coding:utf-8 -*-


import queue
import time

from Class.WCThread import WCThread
from Class.WCMysql import WCMysql
from Class.WCFile import WCFile

SHARE_Q = queue.Queue()  # 构造一个不限制大小的的队列
_WORKER_THREAD_NUM = 1  # 设置worker线程数
_FARMER_THREAD_DELAY = 1  # 秒 设置 worker 线程休眠时间
_FARMER_THREAD_NUM = 1  # 设置farmer线程数

# 运行的参数
_FARMER_MARK = 10
_FARMER_MARK_END = 100

# Mysql 连接
MYSQL_CONNECTION = None
# File
FILE_CONNECTION = None


def farmer_do_something(connection, number):
    item = connection.select('id', 'img').table('movie').where('id', number).get()
    return item


def farmer():
    global _FARMER_MARK
    global _FARMER_MARK_END
    global SHARE_Q
    global MYSQL_CONNECTION
    result = farmer_do_something(MYSQL_CONNECTION, _FARMER_MARK)
    while _FARMER_MARK < _FARMER_MARK_END and result:
        SHARE_Q.put(result)
        _FARMER_MARK += 1
        result = farmer_do_something(MYSQL_CONNECTION, _FARMER_MARK)


def worker_do_something(item, file, connection):
    """
    运行逻辑, 比如抓站
    """
    name = file.uri(item[1]).download()
    if name:
        connection.table('movie').where('id', item[0]).update([['img', name]])


def prn_obj(obj):
    print('\n'.join(['%s:%s' % item for item in obj.__dict__.items()]))


def worker():
    """
    主要用来写工作逻辑, 只要队列不空持续处理
    队列为空时, 检查队列, 由于Queue中已经包含了wait,
    notify和锁, 所以不需要在取任务或者放任务的时候加锁解锁
    """
    global SHARE_Q
    global FILE_CONNECTION
    global MYSQL_CONNECTION
    while not SHARE_Q.empty():
        item = SHARE_Q.get()  # 获得任务
        worker_do_something(item, FILE_CONNECTION, MYSQL_CONNECTION)
        time.sleep(_FARMER_THREAD_DELAY)
        SHARE_Q.task_done()


def main():
    global SHARE_Q
    global MYSQL_CONNECTION
    global FILE_CONNECTION
    workers = []
    farmers = []
    # 向队列中放入任务, 真正使用时, 应该设置为可持续的放入任务

    # 建立Mysql连接
    MYSQL_CONNECTION = WCMysql('222.222.222.201', 'root', 'mao555hg', 'movie')
    # File操作对象
    FILE_CONNECTION = WCFile()
    FILE_CONNECTION.set_dir('./public/image/')

    # 开启farmer线程
    for i in range(_FARMER_THREAD_NUM):
        farmer_thread = WCThread(farmer)
        farmer_thread.start()
        farmers.append(farmer_thread)
    for farmer_thread in farmers:
        farmer_thread.join()
    # 开启worker线程
    for i in range(_WORKER_THREAD_NUM):
        worker_thread = WCThread(worker)
        worker_thread.start()  # 线程开始处理任务
        workers.append(worker_thread)
    for worker_thread in workers:
        worker_thread.join()
    # 等待所有任务完成
    SHARE_Q.join()


if __name__ == '__main__':
    main()
