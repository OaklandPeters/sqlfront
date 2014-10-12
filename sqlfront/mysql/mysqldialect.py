from __future__ import absolute_import
import MySQLdb
from ..interfaces import SQLDialect

class MySQLDialect(SQLDialect):
    @classmethod
    def escape(cls, obj):
        return MySQLdb.escape_string(str(obj))
    @classmethod
    def format(cls, command, *args, **kwargs):
        fargs = [cls.escape(arg) for arg in args]   # pylint: disable=E1120
        fkwargs = dict(
            (key, cls.escape(value))                # pylint: disable=E1120
            for key, value in kwargs.items()
        )
        return command.format(*fargs, **fkwargs)    # pylint: disable=W0142
