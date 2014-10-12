from abc import ABCMeta, abstractproperty, abstractmethod
from .sqldialect import SQLDialect
from .sqlerror import SQLClosingError

__all__ = ['SQLConnection']

class SQLConnection(SQLDialect):
#    __metaclass__ = ABCMeta #Should already have ABCMeta from SQLDialect
    
    # Establishing & querying connection
    opened = abstractproperty(lambda self: NotImplemented)
    open  = abstractmethod(lambda self: NotImplemented)
    close = abstractmethod(lambda self: NotImplemented)

    # Running queries and transactions
    execute = abstractmethod(lambda self, command, parameters: NotImplemented)
    results = abstractmethod(lambda self: NotImplemented)
    commit = abstractmethod(lambda self: NotImplemented)

    # Core connection objects
    cursor = abstractproperty(lambda self: NotImplemented)
    connection = abstractproperty(lambda self: NotImplemented)
    
    # Exceptions
    #SQLExceptionType = abstractproperty(lambda self: NotImplemented)
    #SQLDialectException = abstractproperty(lambda self: NotImplemented)
    
    #    Mixin Methods
    def closed(self):
        """Predicate. Is the connection closed?"""
        return not self.opened
    def __bool__(self):
        return self.opened
    def __enter__(self, *args, **kwargs):
        return self
    def __exit__(self, exception_type, exception_value, traceback):
        try:
            self.close()    #pylint: disable=no-value-for-parameter
        except SQLClosingError:
            # Not closable
            return True
    def run(self, command, parameters=None):
        """Sugar for combining .execute(command) and .results() for simplicity of writing."""
        self.execute(command, parameters)   # pylint: disable=E1120
        return self.results()   # pylint: disable=E1120
