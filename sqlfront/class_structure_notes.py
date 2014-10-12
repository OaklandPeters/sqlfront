"""
Light weight Pythonic interface to SQL (~MySQL only for now).


@todo: Refactor for 'templating' not immediate executions, like an ORM. Desired usage:
    cxn.select(...).run(...)
    Methods which would normally invoke a command (.execute/.run),
    instead return a string-like object, but which has ability to be executed.
    ... proposed classes, this may/may-not be overcomplicated
    @todo SQLConnection - interface, extracted from current SQLInterface
        .connection, .run, .execute, .result
    @todo SQLSyntax - interface. str.
        Maybe not needed (SQLInterface + SQLCommand cover it)
    @todo SQLCommand - interface. str + SQLConnection
        Returned from SQLInterface methods
    @todo MySQLConnection - SQLConnection
    @todo MySQLInterface - SQLInterface
    @todo MySQLCommand - SQLCommand
    @todo MySQL - MySQLInterface + MySQLConnection
@todo: ... probably benefit from turning mysql.py into a package
@todo Add __subclasshook__ for all of the Abstract classes

[] Restructure folders, for mature distribution: sqlwrap is package
sqlwrap/
  sqlwrap/
    __init__.py
    interfaces/
      SQLInterface
      SQLConnection
      SQLCommand
      SQLSyntax
    mysql/
      MySQLConnection
      MySQLInterface
      MySQLCommand
      MySQLSyntax # Non-inherited. Used internally to form commands.
      MySQL  # User interacts with this
    test/
      testing.py  # Support functions
      test_sqldialect.py
      test_mysqlconnection.py
      test_mysql.py
      test_mysql_example.py  # Core example of actual usage
      pylint_mysql.txt
    util/
      # Put rich_X.py functions here
      # Also _read_config, _first, _singleton
    dispatch/
      # 
    drafts/
      # Experimental
    docs/
      # Fill in later
      # Use Sphinx theme and 'Read the Docs' (.org)
  .gitignore
  .LICENSE.txt
  MANIFEST.in
  README.md
  setup.py

    @todo: Write unittests for most functions.
        ESPECIALLY: insertion, and SEVERAL selects
@todo: Fix up to resist mysql-injection.
    Replaces: cmd = "template".format(variables)
              self.run(cmd)
    With:     self.run(template, variables)
    NOTE: MySQLdb expects escape to be '%s' rather than '{0}/{1}' style.
    @todo: Assemble list of methods which will have to change formatting to
        new style (run search for .format).
    @todo: Add step which quietly complains (warning?) when you don't use
        protected variables form
@todo: Make *many* of these functions return self, to enable chaining.
@todo: abstract out the sql-commands functions
    ex. _clause parts, the .format()
@todo: Switch more of these functions to using the 'Qualified' operator.
"""
__version__ = '0.2'
import os, sys
import collections, warnings
import json
from abc import ABCMeta, abstractmethod, abstractproperty
#----- Package Modules
#import aliased #pylint: disable=relative-import
import extern.rich_core as rich_core
import extern.rich_property as rich_property





class SQLException(Exception):
    """Base type for all SQLExceptions.
    Dialects should define their own children.
    @todo: Move this into a subfile
    """
    pass




class SQLImplementation(object):
    """All class objects derived for a particular SQL implementation, should
    be derived from the same child of this.
    
    For example, all MySQL classes should inherit from 
    MySQLLanguage
    """
    __metaclass__ = ABCMeta
    name = abstractproperty(lambda: NotImplemented) #ex. 'MySQL' etc
    @classmethod
    def __subclasshook__(cls, subklass):
        if cls is SQLConnection:
            if all(_hasattr(subklass, attr) for attr in cls.__abstractmethods__):
                return True
        return NotImplemented

class SQLConnection(object):
    __metaclass__ = ABCMeta
    
    # Establishing & querying connection
    opened = abstractproperty(lambda self: NotImplemented)
    initialize = abstractmethod(lambda self, **params: NotImplemented)
    open  = abstractmethod(lambda self: NotImplemented)
    close = abstractmethod(lambda self: NotImplemented)

    # Running queries and transactions
    execute = abstractmethod(lambda self, command, params: NotImplemented)
    results = abstractmethod(lambda self: NotImplemented)
    commit = abstractmethod(lambda self: NotImplemented)

    # Properties
    cursor = abstractproperty(lambda self: NotImplemented)
    connection = abstractproperty(lambda self: NotImplemented)
    
    # Exceptions
    SQLExceptionType = abstractproperty(lambda self: NotImplemented)
    SQLDialectException = abstractproperty(lambda self: NotImplemented)
    
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
        except self.SQLExceptionType:
            # Not closable
            return True
    def run(self, command, params=None):
        """Sugar for combining .execute(command) and .results() for simplicity of writing."""
        self.execute(command, params)   # pylint: disable=E1120
        return self.results()   # pylint: disable=E1120
    #----- Check whether class meets this ABC
    @classmethod
    def __subclasshook__(cls, subklass):
        if cls is SQLConnection:
            if all(_hasattr(subklass, attr) for attr in cls.__abstractmethods__):
                return True
        return NotImplemented


class SQLInterface(object):
    __metaclass__ = ABCMeta
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

    # Exceptions
    SQLExceptionType = abstractproperty(lambda self: NotImplemented)
    exceptions = abstractproperty(lambda self: NotImplemented)
    @classmethod
    def _is_sql_exception(cls, obj):
        """Predicate. Is object a subclass of the root SQL exception
        class for this implementation?
        Ex. for MySQL: MySQLdb.MySQLError
        """
        try:
            return issubclass(obj, cls.SQLExceptionType)
        except TypeError: #obj is not a class object
            return False

    # String Formatting
    @rich_core.abstractclassmethod
    @classmethod
    def escape(cls, obj): #pylint: disable=unused-argument
        """Return a string version of an object, with characters
        escaped appropriately for this langauge."""
        return NotImplemented


    @classmethod
    def format(cls, command, *args, **kwargs):
        """Apply formatting to command, after escaping all arguments."""
        fargs = [cls.escape(arg) for arg in args]   # pylint: disable=E1120
        fkwargs = dict(
            (key, cls.escape(value))                # pylint: disable=E1120
            for key, value in kwargs.items()
        )
        return command.format(*fargs, **fkwargs)    # pylint: disable=W0142
    @classmethod
    def __subclasshook__(cls, subklass):
        if cls is SQLConnection:
            if all(_hasattr(subklass, attr) for attr in cls.__abstractmethods__):
                return True
        return NotImplemented



class SQLCursor(SQLConnection, SQLInterface):
    """User's interface.
    Dialect specific versions of this are simply named after the dialect.
    Example: MySQL instead of MySQLCursor
    
    
    """
    __metaclass__ = ABCMeta
    def __subclasshook__(self):
        
class SQLSyntax(object):
    """Factory functions for constructing parts."""
    where = rich_core.abstractclassmethod(lambda cls, data=None: NotImplemented)
    limits = rich_core.abstractclassmethod(lambda cls, limits=None: NotImplemented)
    compose = rich_core.abstractclassmethod(
        lambda cls, *clauses, **format_inserts: NotImplemented
    )
    
    
class SQLCommand(str):
    """
    Should support optionally passing in, or storing 'params'.
    This requires integrating with SQLSyntax
    ... and some thought
    """
    def __new__(cls, cursor, *args, **kwargs):
        newobj = str.__new__(cls, *args, **kwargs)
        newobj.cursor = cursor
        return newobj
    # cursor is a SQLCursor
    @rich_property.VProperty
    class cursor(object):
        """Cursor to a SQL database."""
        #Should this actually be a Simpleproperty?
        def getter(self):
            return self._cursor
        def setter(self):
            self._cursor = value
        def validator(self, value):
            rich_core.AssertKlass(value, SQLCursor, name='cursor')
            return value
    #---- Mixin methods
    def execute(self, params=None):
        return self.cursor.execute(self, params)
    def results(self):
        return self.cursor.results()
    def run(self, params=None):
        return self.cursor.run(self, self.params)






















#==============================================================================
#        SQL SQLInterface ABC
#==============================================================================
class SQLInterface(object):
    """SQLInterface for implementations of various SQL langauges; for example
    MySQL and SQLite.
    """
    __metaclass__ = ABCMeta
    def __init__(self, *positional, **keywords):    # pylint: disable=W0613
        self._connection = None
        self._cursor = None

    # Establishing & querying connection
    opened = abstractproperty(lambda self: NotImplemented)
    initialize = abstractmethod(lambda self, **params: NotImplemented)
    open  = abstractmethod(lambda self: NotImplemented)
    close = abstractmethod(lambda self: NotImplemented)

    # Running queries and transactions
    execute = abstractmethod(lambda self, command, params: NotImplemented)
    results = abstractmethod(lambda self: NotImplemented)
    commit = abstractmethod(lambda self: NotImplemented)

    # Properties
    @property
    def cursor(self):
        """Basic getter for cursor property."""
        return self._cursor
    @cursor.setter
    def cursor(self, value):
        """Basic setter for cursor property."""
        self._cursor = value
    @property
    def connection(self):
        """Basic getter for connection property."""
        return self._connection
    @connection.setter
    def connection(self, value):
        """Basic setter for connection property."""
        self._connection = value

    #    Mixin Methods
    def __bool__(self):
        """MySQL_Connection() object considered true when connection is open. """
        # Mixin Method: only uses abstract property: self.opened
        return self.opened
    def __enter__(self, *args, **kwargs):
        """Open context manager."""
        # Mixin Method:
        return self
    def __exit__(self, exception_type, exception_value, traceback):
        """Close context manager."""
        # Mixin Method: only uses abstracts: self.close() and self.SQLExceptionType
        try:
            self.close()    #pylint: disable=no-value-for-parameter
        except self.SQLExceptionType:  # Not closable
            return True
    def closed(self):
        """Predicate. Is the connection closed?"""
        return not self.opened
    def run(self, command, params=None):
        """Sugar for combining .execute(command) and .results() for simplicity of writing."""
        # Mixin Method - only uses abstract methods: .run() and .results()
        self.execute(command, params)   # pylint: disable=E1120
        return self.results()   # pylint: disable=E1120


    
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

    # Exceptions
    SQLExceptionType = abstractproperty(lambda self: NotImplemented)
    exceptions = abstractproperty(lambda self: NotImplemented)
    @classmethod
    def _is_sql_exception(cls, obj):
        """Predicate. Is object a subclass of the root SQL exception
        class for this implementation?
        Ex. for MySQL: MySQLdb.MySQLError
        """
        try:
            return issubclass(obj, cls.SQLExceptionType)
        except TypeError: #obj is not a class object
            return False

    # String Formatting
    @rich_core.abstractclassmethod
    def escape(cls, obj): #pylint: disable=unused-argument
        """Return a string version of an object, with characters
        escaped appropriately for this langauge."""
        return NotImplemented


    @classmethod
    def format(cls, command, *args, **kwargs):
        """Apply formatting to command, after escaping all arguments."""
        fargs = [cls.escape(arg) for arg in args]   # pylint: disable=E1120
        fkwargs = dict(
            (key, cls.escape(value))                # pylint: disable=E1120
            for key, value in kwargs.items()
        )
        return command.format(*fargs, **fkwargs)    














#==============================================================================
#    Qualified Reference/Name Object
#==============================================================================
class Qualified(object):
    """Builds fully qualified names for MySQL structures (primarily tables and columns).
    Can include alias.

    >>> Qualified(database=None, table='chemicals')
    chemicals
    >>> Qualified(database='drug_db', table='chemicals')
    drug_db.chemicals
    >>> Qualified(database='drug_db', table='chemicals', column='chem_id', alias='cid')
    drug_db.chemicals.chem_id as cid
    >>> Qualified('drug_db', 'chemicals', 'chem_id', 'cid')
    drug_db.chemicals.chem_id as cid

    >>> "DESCRIBE {0}".format(Qualified(database='drug_db', table='chemicals'))
    'DESCRIBE drug_db.chemicals'
    >>> Qualified(None, None)
    Traceback (most recent call last):
    AssertionError: At least one of must be provided: database, table, or column.

    @todo: Inherit from string/basestring
    @todo: Consider overriding __new__ so this returns a basestring.
    """
    def __init__(self, database=None, table=None, column=None, alias=None):
        #[] Validation - for nullable strings
        nullable = (type(None), basestring)
        rich_core.AssertKlass(database, nullable)
        rich_core.AssertKlass(table, nullable)
        rich_core.AssertKlass(column, nullable)
        rich_core.AssertKlass(alias, nullable)
        #At least one must be present: database, table, column
        isstr = lambda obj: isinstance(obj, basestring)
        assert(any([isstr(database), isstr(table), isstr(column)])), (
            "At least one of must be provided: database, table, or column."
        )

        self.database = database
        self.table = table
        self.column = column
        self.alias = alias

    def __repr__(self):
        qual_name = '.'.join([elm for elm
            in [self.database, self.table, self.column]
            if elm != None])
        if self.alias != None:
            return qual_name + " as " + self.alias
        else:
            return qual_name
    def __str__(self):
        return repr(self)




#==============================================================================
#    SQL Statement Helper
#==============================================================================
class Syntax(object):
    """Convience-class; used to compose the syntax of SQL queries."""
    @classmethod
    def where(cls, data=None):
        """
        'iterable' specifies {column}={value} pairs.
        Either as an iterable of pairs, or as a dict.

        >>> data = {"cid":"20381", "cd_molweight":"381.2", "LogP":"-2.2"}
        >>> Syntax.where(data)
        "WHERE cd_molweight = '381.2' AND LogP = '-2.2' AND cid = '20381'"
        """
        #[] Validation
        valid_types = (type(None), collections.Mapping, rich_core.NonStringIterable)
        rich_core.AssertKlass(data, valid_types)

        if isinstance(data, type(None)):
            return ""
        #Make Iterator ~ Dispatch on Dict or sequence of pairs
        else:
            if isinstance(data, collections.Mapping):
                iterator = iter(data.items())
            else:   #isinstance(data, rich_core.NonStringIterable):
                iterator = ((col, val) for col, val in data.items())

            parts = [
                "{0} = '{1}'".format(col, escape(val))
                for col, val in iterator
            ]
            return "WHERE "+ " AND ".join(parts)
    @classmethod
    def limit(cls, limits=None):
        """Apply a limit clause."""
        if isinstance(limits, type(None)):
            return ""
        elif isinstance(limits, collections.Sequence):
            if len(limits) == 1:
                return "LIMIT {0}".format(limits[0])
            elif len(limits) == 2:
                return "LIMIT {0}, {1}".format(limits[0], limits[1])
            else:
                raise ValueError("Invalid 'limits' length: must be 1 or 2.")
        elif isinstance(limits, (basestring, int)):
            return "LIMIT "+str(limits)
        else:
            raise TypeError("Expected None, Sequence, basestring, or int.")
    @classmethod
    def compose(cls, *clauses, **format_inserts):
        '''Turn SQL clauses into a single statement string,
        formatted for readability, and removing empty clauses.
            Keyword arguments are applied as formatting ~clause.format(kwarg).Example:

        >>> Syntax.compose(
        ...     "SELECT *",
        ...     "FROM {table}",
        ...     "{where}",
        ...     "LIMIT 1",
        ...     table='protein', where=''
        ... )
        'SELECT *\\nFROM protein\\nLIMIT 1;\\n'
        '''
        #[] Apply formatting (which may make some parts empty)
        parts = [part.format(**format_inserts) for part in clauses]

        #[] Filter out empty parts
        parts = [part for part in parts if part not in (None, '')]

        #[] Ensure that sequence ends with ';\n'
        if parts[-1].endswith(';'):
            parts[-1] += '\n'
        elif parts[-1].endswith(';\n'):
            pass
        elif parts[-1].endswith('\n'):
            parts[-1] = parts[-1][:-1]+';\n'
        else:
            parts[-1] += ';\n'
        phrase = '\n'.join(parts)
        return phrase


#==============================================================================
#        convenience Functions
#==============================================================================
def _first(iterable):
    """Return first element of an iterable."""
    return next(iter(iterable))
def _singleton(results):
    """Get first value. Used repetively for queries returning a single
    piece of data.

    >>> results = ({'count(*)': 1L}, )
    >>> _singleton(results)
    1L
    
    @todo Rename this to _first_result(). 'singleton' has preexisting meaning.
    """
    return _first(_first(results).values())

def escape(obj, connection=None):
    """Return object as a string, with characters escaped.
    If connection provided, escapes as per that connection. Else uses default
    MySQL escaping."""
    if connection == None:
        return MySQLdb.escape_string(str(obj))
    elif hasattr(connection, 'escape_string'):
        return connection.escape_string(str(obj))
    elif hasattr(connection, 'escape'):
        return connection.escape(obj)
    else:
        raise TypeError("connection does not have an escape or escape_string function")

def _to_string(data):
    '''Converts potentially abstract objects to strings.
    Commonly used to convert JSON to dicts.
    @todo: type(data) for the Iterable case is wrong, since there
        is no garuntee that type(data)(...) is a valid constructor.'''
    if isinstance(data, unicode):
        return str(data)
    elif isinstance(data, collections.Mapping):
        #return dict(map(_to_string, data.iteritems()))
        return dict(_to_string(item) for item in data.iteritems())
    elif isinstance(data, collections.Iterable):
        #return type(data)(map(_to_string, data))
        return type(data)(_to_string(elm) for elm in data)
    else:
        return data
def _read_json(file_name):
    '''note: to turn resultant dictionary into local variables
    (inside the calling function), have the calling function execute:
    locals().update(_conf)
    '''
    config = json.load(open(file_name))
    return _to_string(config)
def _read_config(path=None):
    """Read a JSON configuration file."""
    if path == None:
        return {}
    else:
        assert(os.path.exists(path)), (
            "Path '{0}' does not exist.".format(path)
        )
        return _read_json(path)
def _hasattr(subklass, attr):
    """Determine if subklass, or any ancestor class, has an attribute.
    Copied shamelessly from the abc portion of collections.py.
    """
    try:
        return any(attr in B.__dict__ for B in subklass.__mro__)
    except AttributeError:
        # Old-style class
        return hasattr(subklass, attr)



class MySQLInterface(SQLInterface):
    """
    This actually implements the abstracts.
    """

class MySQLConnection(SQLConnection):
    """Concrete class implementing the abstracts."""

class MySQL(MySQLConnection, MySQLInterface):
    """Concrete class employed by user."""



if __name__ == "__main__":
    import doctest
    doctest.testmod()

    def doc_check(func):
        """Use to check specific functions, or get more information
        on why they failed the doctest."""
        doctest.run_docstring_examples(func, globals())
