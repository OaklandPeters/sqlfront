from abc import ABCMeta, abstractproperty, abstractmethod
from .sqldialect import SQLDialect
from ..extern.stringtemplate import StringTemplate

__all__ = ['SQLCommand']

class SQLCommand(SQLDialect, StringTemplate):
    __metaclass__ = ABCMeta
    def format(self, *args, **kwargs):
        return SQLDialect.format(self, *args, **kwargs)
