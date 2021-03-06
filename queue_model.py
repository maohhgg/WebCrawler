#!/usr/bin/env python
# -*- coding:utf-8 -*-


import queue
import time

from Class.WCThread import WCThread
from Class.WCMysql import WCMysql
from Class.WCFile import WCFile
from douban import douban

SHARE_Q = queue.Queue()  # 构造一个不限制大小的的队列

# 设置worker线程数
_WORKER_THREAD_NUM = 1
_WORKER_THREAD_DELAY = 0.5  # 秒 设置 worker 线程休眠时间 = 1  # 秒 设置 worker 线程休眠时间

# 设置farmer线程数
_FARMER_THREAD_NUM = 1

# 运行的参数
# _FARMER_MARK = 21431
# _FARMER_MARK_END = 22800

# Mysql 连接
MYSQL_CONNECTION = None
# File
FILE_CONNECTION = None


def farmer_do_something(connection, number):
    """
    通过获取数据库中的 movie库 movie表 img的值
    写入队列
    :param connection:
    :param number:
    :return:
    """
    item = connection.select('id', 'douban').table('movie').where('description', '=', "").all()
    return item


def farmer():
    # global _FARMER_MARK
    # global _FARMER_MARK_END
    global SHARE_Q
    global MYSQL_CONNECTION
    result = farmer_do_something(MYSQL_CONNECTION, 0)
    # SHARE_Q.put(result)
    for p in result:
        print(p)
        SHARE_Q.put(p)


def worker_do_something(item, file, connection):
    """
    读取队列中的img 下载，并更新数据库（把下载链接换成文件名）
    :param item:
    :param file:
    :param connection:
    :return:
    """
    # name = file.uri(item[1]).download(item[0])
    url = 'https://movie.douban.com/subject/%s/' % (item[1])
    cookies = ['cookies',
               'bid=YK3_Rwx8jE4; ll="118318"; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1512345665%2C%22https%3A%2F%2Fwww.douban.com%2F%22%5D; ap=1; _pk_id.100001.4cf6=9ecfeaf49f97bab3.1511954736.7.1512347818.1512234123.; _pk_ses.100001.4cf6=*; __utma=30149280.1818481521.1511694241.1512233975.1512345665.8; __utmb=30149280.0.10.1512345665; __utmc=30149280; __utmz=30149280.1511694241.1.1.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utma=223695111.1889745337.1511954736.1512233975.1512345665.7; __utmb=223695111.0.10.1512345665; __utmc=223695111; __utmz=223695111.1512230764.5.4.utmcsr=douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; _vwo_uuid_v2=1B8F7FC4A70304978ABE8206EA0F8D4E|61ec45fb1b365fb26f2769fa67afeb48']
    file.get(url, cookies)
    name = file.get_description()
    print("%d: %s done" % (item[0],item[1]))
    if name:
        connection.table('movie').where('id', item[0]).update([['description', name]])


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
    global DOUBAN_CONNECTION
    global MYSQL_CONNECTION
    while not SHARE_Q.empty():
        item = SHARE_Q.get()  # 获得任务
        worker_do_something(item, DOUBAN_CONNECTION, MYSQL_CONNECTION)
        time.sleep(_WORKER_THREAD_DELAY)
        SHARE_Q.task_done()


def main():
    global SHARE_Q
    global MYSQL_CONNECTION
    global FILE_CONNECTION
    global DOUBAN_CONNECTION
    workers = []
    farmers = []
    # 向队列中放入任务, 真正使用时, 应该设置为可持续的放入任务

    # 建立Mysql连接
    MYSQL_CONNECTION = WCMysql('222.222.222.201', 'root', 'mao555hg', 'wechat')
    # File操作对象
    FILE_CONNECTION = WCFile()
    FILE_CONNECTION.set_dir('./public/image/')

    DOUBAN_CONNECTION = douban()

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
