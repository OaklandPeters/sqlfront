"""
Light weight Pythonic interface to SQL (~MySQL only for now).


@todo: Refactor for 'templating' not immediate executions, like an ORM. Desired usage:
    cxn.select(...).run(...)
    Methods which would normally invoke a command (.execute/.run),
    instead return a string-like object, but which has ability to be executed.
    ... proposed classes, this may/may-not be overcomplicated
    @todo SQLConnection - interface, extracted from current SQLDialect
        .connection, .run, .execute, .result
    @todo SQLSyntax - interface. str.
        Maybe not needed (SQLDialect + SQLCommand cover it)
    @todo SQLCommand - interface. str + SQLConnection
        Returned from SQLDialect methods
    @todo MySQLConnection - SQLConnection
    @todo MySQLDialect - SQLDialect
    @todo MySQLCommand - SQLCommand
    @todo MySQL - MySQLDialect + MySQLConnection
@todo: ... probably benefit from turning mysql.py into a package
[] Restructure folders, for mature distribution: sqlwrap is package
sqlwrap/
  sqlwrap/
    __init__.py
    interfaces/
      SQLDialect
      SQLConnection
      SQLCommand
      SQLSyntax
    mysql/
      MySQLConnection
      MySQLDialect
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
#----- 3rd party modules
import MySQLdb
#----- Custom modules
import aliased #pylint: disable=relative-import
import local_packages.rich_core as rich_core #pylint: disable=relative-import
import local_packages.rich_property as rich_property






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
        except self.SQLExceptionType:  # Not closable
            return True
    def run(self, command, params=None):
        """Sugar for combining .execute(command) and .results() for simplicity of writing."""
        self.execute(command, params)   # pylint: disable=E1120
        return self.results()   # pylint: disable=E1120

class SQLDialect(object):
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

class SQLCursor(SQLConnection, SQLDialect):
    """User's interface.
    """

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
    def __new__(cls, connection, *args, **kwargs):
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
#        SQL Interface ABC
#==============================================================================
class SQLDialect(object):
    """Interface for implementations of various SQL langauges; for example
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
        return command.format(*fargs, **fkwargs)    # pylint: disable=W0142



#==============================================================================
#            MySQL
#==============================================================================
@aliased.aliased
class MySQL(SQLDialect):
    '''Convience/wrapper class for MySQL-access.
    Considerably lighter-weight than a convential ORM (such as SQLAlchemy).
    '''
    def __init__(self, **keywords):
        """
        Parameters:
        host, user, passwd, default_db
        config: path of JSON configuration file. This is an alternative to
            directly supplying host, user, passwd, and default_db information.
        warnings: whether or not warnings will be shown when executing SQL via
            .run() or .execute() is...
        """
        super(MySQL, self).__init__(**keywords)

        self._parameters = self._validate(**keywords)


        self.cursor, self.connection = self.initialize(**self._parameters) # pylint: disable=W0142

    def _validate(self, **keywords):    # pylint: disable=R0201
        """Validate input keywords, for type and default values."""
        if 'db' in keywords:
            keywords['default_db'] = keywords.pop('db')
        if 'database' in keywords:
            keywords['default_db'] = keywords.pop('database')
        if 'password' in keywords:
            keywords['passwd'] = keywords.pop('password')

        if 'config' in keywords:
            config = _read_config(keywords.pop('config'))
        else:
            config = {}

        #Combine config file with keywords and set defaults
        parameters = rich_core.defaults(keywords, config, {
            'unix_socket':              None,
            'warnings':                 True,
        })


        rich_core.AssertKeys(parameters,
            ['host', 'user', 'passwd', 'default_db'], name='parameters'
        )
        if 'linux' in sys.platform:
            assert(parameters['unix_socket'] != None), (
                "Missing unix_socket parameter - required for MySQL"
                " connection on Linux systems."
            )

        return parameters


    #--------------- Initialization
    @classmethod
    def initialize(cls, **params):
        """Initialize the connection's cursor and connection objects."""
        connection = MySQLdb.connect(
            params['host'], params['user'], params['passwd'],
            unix_socket=params['unix_socket']
        )
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        if params.get('default_db', None) != None:
            cursor.execute("USE {0}".format(params['default_db']))
        return (cursor, connection)
    @classmethod
    def initialize_parameters(cls, **params):
        """An alias of initialize(), would use @aliased.alias - but that decorator
        fails for classmethods."""
        return cls.initialize(**params)


    #==============================================================================
    #         Establishing & querying connection
    #==============================================================================
    def open(self, **keywords):
        """Open the connection, based on connection parameters specified in keywords.
        Note: this is a more modern version of initialize().
        """
        params = {}.update(self._parameters, **keywords)
        connection = MySQLdb.connect(
            params['host'], params['user'], params['passwd'],
            unix_socket=params['unix_socket']
        )
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        if params.get('default_db', None) != None:
            cursor.execute("USE {0}".format(params['default_db']))
        return (cursor, connection)
    def close(self):
        """Close the cursor and the connection objects."""
        self.cursor.close()
        self.connection.close()
    @property
    def opened(self):
        """Predicate. Is the connection open?"""
        return bool(self.connection.open)
#     #    Context Manager
#     def __enter__(self, *args, **kwargs):
#         return self
#     def __exit__(self, exception_type, exception_value, traceback):
#         try:
#             self.close()
#         except MySQLdb.ProgrammingError:
#             #Not closable
#             return True


    #==============================================================================
    #        Running queries and transactions
    #==============================================================================
    def execute(self, sql_command, params=None):
        """Execute a command, accepts params to insert into command
        (used to combat sql-inject).
        """
        with warnings.catch_warnings():
            ret_val = self.cursor.execute(sql_command, params)
        return ret_val
    @aliased.alias('get_results')
    def results(self):
        """Fetch results from last query."""
        return self.cursor.fetchall()
    def commit(self):
        """Commit any pending results to the database."""
        self.connection.commit()
        return self

    @aliased.alias('insert_dict')
    def insert(self, table, data, database=None):
        '''Adds contents of data (mapping, ~dict) to a table. keys() define columns.'''
        rich_core.AssertKlass(data, collections.Mapping, name='data')
        table_name = Qualified(database=database, table=table)
        table_columns = self.columns(table_name)
        # Filter out data keys (~columns) not in the table
        valid_data = dict(
            (k, v) for k, v in data.items()
            if k in table_columns
        )
        if valid_data == {}:
            return None
        else:
            sql_insert = (
                "INSERT INTO {table} ({columns}) "
                "VALUES ('{values}');"
                ).format(
                    table   = table_name,
                    columns = ', '.join(str(k) for k in valid_data.keys()),
                    values  = "', '".join(str(v) for v in valid_data.values())
                )
            self.run(sql_insert)
            return sql_insert
    def select(self, tables, columns='*', where=None, limit=None):
        '''
        if columns is list/tuple --> SELECT {columns}
        if columns is dict --> SELECT {columns.keys()} WHERE
        '''
        tables = rich_core.ensure_tuple(tables)
        columns = rich_core.ensure_tuple(columns)

        rich_core.AssertKlass(columns, (collections.Mapping, rich_core.NonStringIterable))
        #if columns  is a data dict
        if isinstance(columns, collections.Mapping):
            assert(where is None), (
                "If 'columns' is a dict, then a 'where' input should not be provided."
            )
            sql_select = Syntax.compose(
                "SELECT "+', '.join(str(k) for k in columns),
                "FROM "+', '.join(k for k in tables),
                Syntax.where(columns),
                Syntax.limit(limit)
            )
        elif isinstance(columns, rich_core.NonStringIterable):

            rich_core.AssertKlass(where, (collections.Mapping, type(None)), name='where')
            if where == None:
                sql_select = Syntax.compose(
                    "SELECT "+', '.join(str(k) for k in columns),
                    "FROM "+', '.join(k for k in tables),
                )
            sql_select = Syntax.compose(
                "SELECT "+', '.join(str(k) for k in columns),
                "FROM "+', '.join(k for k in tables),
                Syntax.where(where),
                Syntax.limit(limit)
            )

        return self.run(sql_select)



    #==============================================================================
    #         Listing structure names
    #==============================================================================
    @aliased.alias('get_database_names')
    def databases(self):
        """Return the names of all databases visible to the current user."""
        results = self.run("SHOW DATABASES")
        return [row['Database'] for row in results]

    @aliased.alias('get_table_names')
    def tables(self, database=None):
        """Return all tables in a database (or default database if none provided)."""
        if database is None:
            rows = self.run("SHOW TABLES")
        else:
            rows = self.run("SHOW TABLES in "+database)
        return [row.values()[0] for row in rows]

    @aliased.alias('get_column_names')
    def columns(self, table, database=None):
        """Get names of all columns in a table."""
        results = self.run("DESCRIBE {0}".format(
            Qualified(table=table, database=database)
        ))
        column_names = [row['Field'] for row in results]
        return column_names

    @aliased.alias('get_column_types')
    def column_types(self, table, database=None):
        """Return a dict of column names and types for a table."""
        results = self.run(str.format(
            "SHOW FIELDS FROM {0}",
            Qualified(table=table, database=database)
        ))
        return dict((row['Field'], row['Type']) for row in results)

    #==============================================================================
    #         Checking existence of structures
    #==============================================================================
    def exists(self, table=None, database=None, column=None, row=None):
        """Dispatcher function for checking existance of tables, databases,
        columns in tables, and rows in columns."""
        if row != None:
            rich_core.AssertKlass(row, collections.Mapping, name='row')
            rich_core.AssertKlass(table, basestring, name='table')
            rich_core.AssertKlass(database, (type(None), basestring), name='database')
            #Must also have table
            return self._row_exists(row=row, table=table, database=database)
        elif column != None:
            #Must also have table
            return self._column_exists(column, table, database=database)
        elif table != None:
            return self._table_exists(table, database=database)
        elif database != None:
            return self._database_exists(database)
        else:
            #No arguments provided, or all were None
            raise TypeError("No arguments provided, or all were equal to 'None'.")
    @aliased.alias('table_exists')
    def _table_exists(self, table, database=None):
        """Predicate. Does table exist?"""
        if database is None:
            results = self.run("SHOW TABLES LIKE '{0}'".format(table))
        else:
            results = self.run("SHOW TABLES IN {0} LIKE '{1}'".format(database, table))
        return len(results) > 0
    @aliased.alias('column_exists')
    def _column_exists(self, column, table, database=None):
        """Return True if column exists in a given table."""
        table_name = Qualified(table=table, database=database)
        result = self.run("SELECT * FROM {0} LIMIT 1;".format(table_name))
        return (column in _first(result).keys())
    @aliased.alias('row_exists')
    def _row_exists(self, table, data, search_limit=None):
        """Return True if a table contains all data, as specified by a data dictionary."""
        if search_limit != None:
            sql_select = str.format(
                "SELECT * "
                + "FROM (SELECT * FROM {table} LIMIT {search_limit}) as subselect "
                + "{where} "
                + "LIMIT 1",
                table           = table,
                where           = Syntax.where(data),
                search_limit    = str(search_limit)
            )
        else:
            sql_select = str.format(
                "SELECT * FROM {table} "
                + "{where} LIMIT 1",
                table       = table,
                where       = Syntax.where(data)
            )
        results = self.run(sql_select)
        return (len(results) > 0)

    @aliased.alias('database_exists')
    def _database_exists(self, db_name):
        """Predicate. Checks if a database exists."""
        sql_check = str.format(
            "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{0}';",
            db_name
        )
        results = self.run(sql_check)
        if len(results) != 0:
            return True
        else:
            return False


    #==============================================================================
    #        Misc Table Queries
    #==============================================================================
    @aliased.alias('table_size')
    def count(self, table, database=None):
        """Return integer count of number of results in table.
        @todo: Generalize with a data parameter ~ where clause (use Syntax.where)"""
        results = self.run("SELECT count(*) FROM {0};".format(
            Qualified(table=table, database=database)
        ))
        #if no results found
        if not len(results):
            return 0
        # Wrangle out results
        else:
            return int(_singleton(results))
            #Results looks like: ({'count(*)': 24999L}, )
            #--> takes some wrangling
            #return int(_first(_first(results).values()))

    @aliased.alias('pk')
    def primary_key(self, table, database=None):
        """Finds a primary key in database.table."""
        results = self.run("DESCRIBE {0};".format(
            Qualified(database=database, table=table)
        ))
        rows = (row for row in results if row['Key']=='PRI')
        return next(rows)['Field']
    def describe(self, table, database=None):
        """Return information about columns, their types, and specifications for a table."""
        return self.run("DESCRIBE {0};".format(Qualified(database, table)))

    #==============================================================================
    #    Dropping Structures
    #==============================================================================
    def drop(self, table=None, database=None):
        """Dispatcher function to _drop_database(), and _drop_table()."""
        if (table != None):
            self._drop_table(table, database=database)
        elif database != None:
            self._drop_database(database)
    def _drop_database(self, database):
        """Drop a database."""
        self.run("DROP DATABASE {0};".format(database))
    def _drop_table(self, table, database=None):
        """Drop table from default database."""
        self.execute("DROP TABLE {0}".format(Qualified(table=table, database=database)))
        return self


    #==============================================================================
    #    Database-Wide Interaction Functions
    #==============================================================================


    @aliased.alias('create')
    def create_database(self, new_name):
        """Create a database."""
        self.run("CREATE DATABASE {0}".format(new_name))

    def rename_database(self, old_name, new_name):
        """Rename a database."""
        assert(self.database_exists(old_name)), (
            str.format(
                "Database renaming failed, because database '{0}' does not exist.",
                old_name
            )
        )
        assert(not self.database_exists(new_name)), (
            str.format(
                "Database renaming failed, because database '{0}' already exists.",
                new_name
            )
        )

        self.create_database(new_name)
        for table in self.get_table_names(old_name):       #Rename each table
            sql_rename = '''RENAME TABLE {0}.{2} TO {1}.{2};'''.format(old_name, new_name, table)
            self.run(sql_rename)

        self.drop_database(old_name)
    def database(self, database=None):
        """Get current database."""
        rich_core.AssertKlass(database, (type(None), basestring), name='database')
        if database == None:
            result = self.run("SELECT DATABASE();")
            return _singleton(result)
        else:
            self.execute("USE {0};".format(database))
    @property
    def default_db(self):
        """Return default databse, as tracked by the MySQL() Python object.
        (differs from current database in MySQL itself)."""
        database = _singleton(self.run("SELECT DATABASE();"))
        if database in ["null", "NULL", "Null"]:
            return None #No default database set
        return database


    #==============================================================================
    #    Table Functions
    #==============================================================================
    def create_table(self, new_table, like=None, columns=None, primary_key=None):
        '''Create a table.
        'like': used if provided a table name
        'columns': used if string specifying columns
        '''
        assert(bool(like) != bool(columns)), (
            "One, and only one of 'like' or 'columns' should be provided."
        )

        if like:
            assert(self.table_exists(like)), (
                "Table specified by 'like' ({0}) does not exist.".format(like)
            )
            sql_create_insert = (
                "CREATE TABLE {0} LIKE {1};"
                "INSERT {1} SELECT * FROM {0};"
            ).format(new_table, like)
            return self.run(sql_create_insert)
        else:   #assumes
            assert(type(columns) in [list, tuple]), (
                "Columns should be specified as a list or tuple of strings."
            )
            assert(all([type(col)==str for col in columns])), (
                "Not all entries in 'columns' are strings."
            )
            assert(not self.table_exists(new_table)), "Table already exists."

            if primary_key in [None, False]:
                pkey = ""
            else:
                pkey = "    {0}\n".format(primary_key)

            sql_create = (
                "CREATE TABLE {name}(\n"
                "    {all_columns}\n"
                "{pkey});"
            ).format(
                name=new_table,
                all_columns=", \n    ".join(columns),
                pkey=pkey)

            return self.run(sql_create)

    def copy_table(self, old_table, new_table):
        """Create a new table, and copy data and structure of an old table into it."""
        assert(self.table_exists(old_table)), (
            "Copy failed. Existing table '{0}' already exists.".format(old_table)
        )
        assert(not self.table_exists(new_table)), (
            "Copy failed. New table '{0}' already exists.".format(new_table)
        )

        self.create_table(new_table, like=old_table)

    #==============================================================================
    #        Exceptions
    #==============================================================================
    @rich_core.ClassProperty
    @classmethod
    def SQLExceptionType(cls):
        """Return parent class for exceptions of this SQL type."""
        return MySQLdb.MySQLError

    @rich_core.ClassProperty
    @classmethod
    #@property
    def exceptions(cls):
        """Return all MySQL-related exceptions. These should be:
            [MySQLdb.DataError, MySQLdb.DatabaseError, MySQLdb.OperationalError,
            MySQLdb.NotSupportedError, MySQLdb.DataError, MySQLdb.IntegrityError,
            MySQLdb.ProgrammingError, MySQLdb.DatabaseError, MySQLdb.InternalError]
        """
        if not hasattr(cls, '_exceptions'):
            # Cache values
            cls._exceptions = [attr
                for attr in vars(MySQLdb).values()
                if cls._is_mysql_exception(attr)
            ]
        return cls._exceptions



    #==============================================================================
    #    String Escaping Functions
    #==============================================================================
    @classmethod
    def escape(cls, obj):
        """Escape string version of an object, using formatting specified by connection."""
        return MySQLdb.escape_string(str(obj))

    #==============================================================================
    #    Magic Methods
    #==============================================================================
    def __repr__(self):
        return "{name}({parameters})".format(
            type(self).__name__, self._parameters
        )










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








if __name__ == "__main__":
    import doctest
    doctest.testmod()

    def doc_check(func):
        """Use to check specific functions, or get more information
        on why they failed the doctest."""
        doctest.run_docstring_examples(func, globals())
