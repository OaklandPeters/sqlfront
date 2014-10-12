from __future__ import absolute_import
import MySQLdb
from ..interfaces import SQLInterface
from .mysqldialect import MySQLDialect


class MySQLInterface(SQLInterface, MySQLDialect):
    """
    Does not have an __init__
    """
    pass
