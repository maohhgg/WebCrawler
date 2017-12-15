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

    def __init__(self, host, user, password, database, charset="utf8"):
        self.connection = pymysql.connect(
            host, user, password, database, use_unicode=True, charset=charset)
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
        elif args[2]:
            self._where = "`%s` %s %s" % (args[0], args[1], args[2])
        else:
            self._where = str("`%s` = '%s'" % (args[0], args[1]))
        return self

    def update(self, args):
        args = list(args)
        self._update_arr(args)
        self._sql = str('UPDATE `%s` SET %s WHERE %s' % (self._table, self._update, self._where))
        print(self._sql)
        return self._exec()

    def insert(self, args):
        keys = list(args.keys())
        values = list(args.values())
        keys = self._update_keys(keys)
        values = self._update_keys(values, '\'')
        keys = ",".join(keys)
        values = ",".join(map(str, values))
        self._sql = "INSERT INTO %s (%s) VALUES (%s)" % (self._table, keys, values)
        return self._exec()

    def get(self):
        self._sql = "SELECT %s FROM `%s` WHERE %s" % (self._select, self._table, self._where)
        return self._exec()

    def all(self):
        self._sql = "SELECT %s FROM `%s` WHERE %s" % (self._select, self._table, self._where)
        return self._exec(True)

    def _update_keys(self, args, string='`'):
        for i in range(0, len(args)):
            if type(args[i]) == type(str('123')):
                args[i] = "%s%s%s" % (string, args[i], string)
        return args

    def _update_arr(self, args):
        temp = []
        for item in args:
            if type(item[1]) is type(10):
                temp.append(str("`%s` = %d" % (item[0], item[1])))
            else:
                temp.append(str("`%s` = %s" % (item[0], self.connection.escape(item[1]))))
        self._update = ','.join(temp)

    def _exec(self, all=None):
        if self._sql:
            try:
                self.cursor.execute(self._sql)
                self.connection.commit()
                if all:
                    result = self.cursor.fetchall()
                else:
                    result = self.cursor.fetchone()
                return list(result)
            except:
                self.connection.rollback()
