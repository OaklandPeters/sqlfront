from __future__ import absolute_import
from ..interfaces import SQLCommand
from .mysqldialect import MySQLDialect

class MySQLCommand(SQLCommand, MySQLDialect):
    pass
