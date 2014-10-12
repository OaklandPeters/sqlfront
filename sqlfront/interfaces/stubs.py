
__all__ = [
    'SQLDialect',
    'SQLInterface',
    'SQLSyntax',
    'SQLConnection',
    'SQLCommand',
    'SQLCursor',
    'SQLQuery',
    'SQLError'
]

class SQLDialect(object):
    pass 

class SQLInterface(SQLDialect):
    """Set of commands, returning SQLCommand."""

class SQLConnection(SQLDialect):
    """Live connection to SQL."""

class SQLCommand(SQLDialect):
    """A valid SQL-string."""
    
class SQLSyntax(SQLDialect):
    """Factory for forming clauses."""


#-------------- Combined Classes
class SQLCursor(SQLConnection, SQLInterface):
    """Primary user interace. Constructs commands in SQL syntax."""

class SQLQuery(SQLConnection, SQLCommand):
    """Primary action point. Invoked to cause commands to run inside SQL."""



#--------- Miscillany
class SQLError(Exception):
    """Base class for error types."""