from __future__ import absolute_import
from abc import ABCMeta, abstractproperty, abstractmethod
from .sqldialect import SQLDialect

__all__ = ['SQLInterface']

class SQLInterface(SQLDialect):
    """Primary user-interface class."""
    __metaclass__ = ABCMeta

    # A SQLSyntax object. Used to construct & return SQLCommand
    syntax = abstractproperty()

    #Note: this is a variation of existing 'insert' -- it accepts database keyword
    insert = abstractmethod(lambda self, table, data, database=None: NotImplemented)
    select = abstractmethod(lambda self, table, data, database=None: NotImplemented)


    # Listing structure names
    databases = abstractmethod(lambda self: NotImplemented)
    tables = abstractmethod(lambda self, database=None: NotImplemented)
    columns = abstractmethod(lambda self, table, database=None: NotImplemented)

    # Checking existence of structures
    exists = abstractmethod(lambda self, **keywords: NotImplemented)
    _table_exists = abstractmethod(lambda self, table, database=None: NotImplemented)
    _database_exists = abstractmethod(lambda self, database: NotImplemented)
    _column_exists = abstractmethod(lambda self, table, column, database=None: NotImplemented)
    _row_exists = abstractmethod(lambda self, table, column, row, database=None: NotImplemented)

    # Dropping structures
    drop = abstractmethod(lambda self: NotImplemented)
    _drop_table = abstractmethod(lambda self: NotImplemented)
    _drop_database = abstractmethod(lambda self: NotImplemented)

    # Misc table queries
    count = abstractmethod(lambda self, table, database: NotImplemented)
    primary_key = abstractmethod(lambda self, table, database: NotImplemented)
    describe = abstractmethod(lambda self, table, database: NotImplemented)

    # Misc database queries
    create_database = abstractmethod(lambda self, name: NotImplemented)
    rename_database = abstractmethod(lambda self, old, new: NotImplemented)
    create_table = abstractmethod(lambda self, name, **keywords: NotImplemented)
    copy_table = abstractmethod(lambda self, old, new: NotImplemented)
