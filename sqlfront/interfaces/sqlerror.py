
__all__ = ['SQLError', 'SQLClosingError']

class SQLError(Exception):
    pass

class SQLClosingError(SQLError):
    """Error related to closing a connection."""

# Should probably have multiple sub-types
# such as:
# (1) Incorrect argument types to functions
# (2) The command errored while running inside SQL itself