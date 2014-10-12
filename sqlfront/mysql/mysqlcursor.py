from __future__ import absolute_import
from ..interfaces import SQLCursor
from .mysqlinterface import MySQLInterface
from .mysqlconnection import MySQLConnection


class MySQLCursor(SQLCursor, MySQLConnection, MySQLInterface):
    pass
