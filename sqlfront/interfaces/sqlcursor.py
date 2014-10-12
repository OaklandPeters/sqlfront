from __future__ import absolute_import
from abc import ABCMeta, abstractproperty, abstractmethod
from .sqlconnection import SQLConnection
from .sqlinterface import SQLInterface

__all__ = ['SQLCursor']

class SQLCursor(SQLConnection, SQLInterface):
    __metaclass__ = ABCMeta
