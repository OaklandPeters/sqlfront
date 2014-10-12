from __future__ import absolute_import
from abc import ABCMeta, abstractproperty, abstractmethod
from .sqlconnection import SQLConnection
from .sqlcommand import SQLCommand

__all__ = ['SQLQuery']

class SQLQuery(SQLConnection, SQLCommand):
    __metaclass__ = ABCMeta
