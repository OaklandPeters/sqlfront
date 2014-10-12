from __future__ import absolute_import
from ..interfaces import SQLQuery
from .mysqlcommand import MySQLCommand
from .mysqlconnection import MySQLConnection

class MySQLQuery(SQLQuery, MySQLConnection, MySQLCommand):
    pass
