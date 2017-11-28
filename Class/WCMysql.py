#!/usr/bin/env python
# -*- coding:utf-8 -*-
import pymysql


class WCMysql:
    """
    Establish a connection to the MySQL database.

    host: Host where the database server is located
    user: Username to log in as
    password: Password to use.
    database: Database to use, None to not use a particular one.
    """

    def __init__(self, host, user, password, database):
        self.connection = pymysql.connect(
            host, user, password, database, use_unicode=True, charset="utf8")
        self.cursor = self.connection.cursor()
        self._sql = False

    def __del__(self):
        self.connection.close()

    def table(self, dbname):
        self._table = str(dbname)
        return self

    def select(self, *args):
        self._select = str(",".join(args))
        return self

    def where(self, *args):
        if type(args[1]) is type(10):
            self._where = str("`%s` = %d" % (args[0], args[1]))
        else:
            self._where = str("`%s` = '%s'" % (args[0], args[1]))
        return self

    def update(self, args):
        args = list(args)
        self.__update(args)
        self._sql = str("UPDATE `%s` SET %s WHERE %s" % (self._table, self._update, self._where))
        return self.__exec()

    def get(self):
        self._sql = str("SELECT %s FROM `%s` WHERE %s" % (
            self._select, self._table, self._where))
        return self.__exec()

    def __update(self, args):
        temp = []
        for item in args:
            if type(item[1]) is type(10):
                temp.append(str("`%s` = %d" % (item[0], item[1])))
            else:
                temp.append(str("`%s` = '%s'" % (item[0], item[1])))
        self._update = ','.join(temp)


    def __exec(self):
        if self._sql:
            try:
                self.cursor.execute(self._sql)
                self.connection.commit()
                result = self.cursor.fetchone()
                return list(result)
            except:
                self.connection.rollback()
