from __future__ import absolute_import
from ..interfaces import SQLError, SQLClosingError


class MySQLError(SQLError):
    pass

class MySQLClosingError(SQLClosingError, MySQLError):
    """Problem with closing a connection or cursor."""
