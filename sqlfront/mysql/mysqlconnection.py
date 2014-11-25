"""
@todo: Move the 'parameters' into independent properties
    host
    user
    password #passwd
    socket #unix_socket
@todo: Type checking for parameters - via properties, on assignment
@todo: If 'database', 'db', etc passed into __init__, call "USE {db}", but do not create a property
@todo: If not linx (sys.platform) -- set unix_socket to None
@todo: Cleanup valid parameters for input.
    'passwd' --> 'password'
    'default_db'&'db' --> 'database'
    (1) Read config if provided
        _password
        _database
        _user
@todo: Add property: warnings (flag)
@todo: Add abstract property to SQLConnection: Warnings
"""
from __future__ import absolute_import
#from abc import ABCMeta, abstractmethod, abstractproperty
import sys
import MySQLdb
from .mysqldialect import MySQLDialect
from .mysqlerror import MySQLClosingError
from ..interfaces import SQLConnection
from ..util.utilities import _read_config
from ..extern import rich_core
from ..extern import clsproperty
from ..extern.nulltype import NotPassed, NotPassedType, NullType
    
class MySQLConnection(SQLConnection, MySQLDialect):
#     # Class-level Defaults for connection parameters
#     _host = "127.0.0.1" #str
#     _user = "root" #str
#     _password = None #nullable str
#     _port = 3306 #nullable int
#     _socket = None #nullable str
#     _database = None #nullable str
# 
#     
# 
#     @property
#     def socket(self):
#         """NoneType or basestring. Location of socket file, on UNIX systems."""
#         return self.socket
#     @socket.setter
#     def socket(self, value):
#         if 'linux' in sys.platform:
#             assert(not isinstance(value, NullType)), (
#                 "Missing unix_socket parameter - required for MySQL"
#                 " connection on Linux systems."
#             )
#         rich_core.AssertKlass(isinstance(value, (type(None), basestring)), name='socket')
#         self._socket = value
    
    
    
    
    def __init__(self, **keywords):
        """
        Parameters:
        host, user, passwd, default_db
        config: path of JSON configuration file. This is an alternative to
            directly supplying host, user, passwd, and default_db information.
        warnings: whether or not warnings will be shown when executing SQL via
            .run() or .execute() is...
        """
        print('--')
        import pdb
        pdb.set_trace()
        print('--')
        
        (self.host, self.user, self.password,
            self.port, self.socket, self.database) = self._validate(**keywords)
        self.cursor, self.connection = self.open()

    
    
    


    def _validate(self, **keywords):    # pylint: disable=R0201
        """Validate input keywords, for type and default values."""
        
        # Aliases for password and default database
        if 'config' in keywords:
            config = _read_config(keywords.pop('config'))
        else:
            config = {}
        #Combine config file with keywords and set defaults
        # self.parameters should return class-level defaults
        parameters = rich_core.defaults(keywords, config, self.parameters)
        
        if 'db' in parameters:
            parameters['database'] = parameters.pop('db')
        if 'default_db' in parameters:
            parameters['database'] = parameters.pop('default_db')
        if 'passwd' in parameters:
            parameters['password'] = parameters.pop('passwd')
        if 'unix_socket' in parameters:
            parameters['socket'] = parameters.pop('unix_socket')
        
        return (parameters['host'], parameters['user'],
            parameters['password'], parameters['port'],
            parameters['socket'], parameters['database'])




    #----------------------------------------------------------------
    # Establishing & querying connection
    #----------------------------------------------------------------
    @property
    def parameters(self):
        """Connection parameters. Values set to None will not be used."""
        return dict(
            host = self.host,
            user = self.user,
            passwd= self.password,
            db = self.database,
            port = self.port,
            unix_socket = self.socket
        )
    @property
    def opened(self):
        """Predicate. Is the connection open?"""
        return bool(self.connection.open)

    def open(self, **keywords):
        """Open the connection, based on connection parameters specified in
        keywords or in self.parameters.
        Note: this is a more modern version of initialize().
        """
        # Combine keywords + parameters
        # Filter out values set to 'None'
        params = dict(
            (key, value) for key, value
            in {}.update(self.parameters, **keywords)
            if not isinstance(value, NullType)
        )
        connection = MySQLdb.connect(**params)
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        if not isinstance(params.get('database', None), NullType):
            cursor.execute("USE {0}".format(params['database']))
        return (cursor, connection)
        

    def open(self, **keywords):
        """Open the connection, based on connection parameters specified in keywords.
        Note: this is a more modern version of initialize().
        """
        params = {}.update(self.parameters, **keywords)
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
        try:
            self.cursor.close()
        except MySQLdb.ProgrammingError:
            raise MySQLClosingError("Could not close cursor.")
        try:
            self.connection.close()
        except MySQLdb.ProgrammingError:
            raise MySQLClosingError("Could not close connection.")
        
    #----------------------------------------------------------------
    # Context managers
    #----------------------------------------------------------------
    def __enter__(self, *args, **kwargs):
        return self
    def __exit__(self, exc_type=NotPassed, exc_value=NotPassed, exc_traceback=NotPassed):
        try:
            self.close()
        except (MySQLClosingError):
            pass
        if exc_type is NotPassed:
            return True
        else:
            return False #re-raise exception

    #----------------------------------------------------------------
    # Running queries and transactions
    #----------------------------------------------------------------
    def execute(self, command, parameters=None):
        """Execute a command, accepts params to insert into command
        (used to combat sql-inject).

        MySQLdb.cursor.execute() returns a 'long' of # rows affected.
        """
        # if self.warnings:
        #     with warnings.catch_warnings():
        #         return self.cursor.execute(command, parameters)
        # else:
        #     return self.cursor.execute(command, parameters)
        return self.cursor.execute(command, parameters)
    def results(self, size=None):
        if isinstance(size, type(None)):
            return self.cursor.fetchall()
        else: # assumes size is an integer
            return self.cursor.fetchmany(size)
    def commit(self):
        """Commit any pending results to the database."""
        return self.connection.commit()
