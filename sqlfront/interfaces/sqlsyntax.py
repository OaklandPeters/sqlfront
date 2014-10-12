from __future__ import absolute_import
from abc import ABCMeta, abstractproperty, abstractmethod
from .sqldialect import SQLDialect

__all__ = ['SQLSyntax']

class SQLSyntax(SQLDialect):
    __metaclass__ = ABCMeta