from __future__ import absolute_import
from ..interfaces import SQLSyntax
from .mysqldialect import MySQLDialect

class MySQLSyntax(SQLSyntax, MySQLDialect):
    pass
