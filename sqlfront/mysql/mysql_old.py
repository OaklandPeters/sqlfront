import MySQLdb

#==============================================================================
#            MySQL
#==============================================================================
@aliased.aliased
class MySQL(SQLInterface):
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