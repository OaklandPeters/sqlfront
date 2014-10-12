from ..interfaces import SQLInterface, SQLSyntax, SQLConnection, SQLCommand, SQLCursor, SQLQuery, SQLDialect, SQLError

__all__ = [
    'MySQLDialect',
    'MySQLInterface',
    'MySQLSyntax',
    'MySQLConnection',
    'MySQLCommand',
    'MySQLCursor',
    'MySQLQuery',
    'MySQLError',
]

class MySQLDialect(SQLDialect):
    """Base class for all MySQL classes.""" 


class MySQLInterface(SQLInterface, MySQLDialect):
    """Set of commands, returning MySQLCommand."""

class MySQLSyntax(SQLSyntax, MySQLDialect):
    """Constructs component clauses of MySQL, returns MySQLCommand."""


class MySQLConnection(SQLConnection, MySQLDialect):
    """Live connection to MySQL."""

class MySQLCommand(SQLCommand, MySQLDialect):
    """A valid MySQL-string."""
    


#-------------- Combined Classes
class MySQLCursor(SQLCursor, MySQLConnection, MySQLInterface):
    """Primary user interace. Constructs commands in MySQL syntax."""

class MySQLQuery(SQLQuery, MySQLConnection, MySQLCommand):
    """Primary action point. Invoked to cause commands to run inside MySQL."""


#--------------- Auxillary Classes
class MySQLError(SQLError):
    """Base Exception type for all MySQL-related Errors."""

