
import queue
import time

from Class.WCThread import WCThread
from Class.WCMysql import WCMysql
from Item.php_net import PHP

if __name__ == '__main__':
    php = PHP()
    php.get('https://goodday.ddns.net/test/function.array-search.php')
    php.get_all()