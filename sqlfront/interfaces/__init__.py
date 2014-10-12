from __future__ import absolute_import

__all__ = [
    'SQLDialect',
    'SQLInterface',
    'SQLSyntax',
    'SQLConnection',
    'SQLCommand',
    'SQLCursor',
    'SQLQuery',
    'SQLError', 'SQLClosingError'
]

from .sqldialect import SQLDialect
from .sqlinterface import SQLInterface
from .sqlsyntax import SQLSyntax
from .sqlconnection import SQLConnection
from .sqlcommand import SQLCommand
from .sqlcursor import SQLCursor
from .sqlquery import SQLQuery

SQLDialect.registry = {
    'dialect': SQLDialect,
    'interface': SQLInterface,
    'syntax': SQLSyntax,
    'connection': SQLConnection,
    'command': SQLCommand,
    'cursor': SQLCursor,
    'query': SQLQuery
}

from .sqlerror import SQLError, SQLClosingError
