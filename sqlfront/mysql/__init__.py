from __future__ import absolute_import

__all__ = [
    'MySQL',
    'MySQLDialect',
    'MySQLInterface',
    'MySQLSyntax',
    'MySQLConnection',
    'MySQLCommand',
    'MySQLCursor',
    'MySQLQuery',
    'MySQLError',
]

# STUBS: Currently importing from stubs. Will be filled as completed
from .stubs import (
    MySQLDialect,
    MySQLInterface,
    MySQLSyntax,
    MySQLConnection,
    MySQLCommand,
    MySQLCursor,
    MySQLQuery,
    MySQLError
)

MySQLDialect.registry = {
    'dialect': MySQLDialect,
    'interface': MySQLInterface,
    'syntax': MySQLSyntax,
    'connection': MySQLConnection,
    'command': MySQLCommand,
    'cursor': MySQLCursor,
    'query': MySQLQuery
}

MySQL = MySQLCursor

from .mysqldialect import SQLDialect
from .mysqlinterface import SQLInterface
from .mysqlsyntax import SQLSyntax
from .mysqlconnection import SQLConnection
from .mysqlcommand import SQLCommand
from .mysqlcursor import SQLCursor
from .mysqlquery import SQLQuery

from .mysqlerror import SQLError
