"""
@todo: Provide alternate dispatches for escape, etc execute(), run()  escape(string, connection)
    Where a *string* is provided, along with a connection

    
"""

from __future__ import absolute_import
from ..interfaces import SQLCursor, SQLQuery, SQLDialect
from ..extern.nulltype import NotPassed, NullType
import local_package.rich_core as rich_core

def escape(command, sqlobj=None):
    """Return object as a string, with characters escaped.
    If connection provided, escapes as per that connection. Else uses default
    MySQL escaping."""
    
    
    return command.escape()
    
    if isinstance(sqlobj, SQLDialect):
    
    if isinstance(sqlobj, NullType): #No sqlobj provided
        # command is a sqlobject, and has 'escape' method
        if isinstance(command, SQLDialect) and hasattr(command, 'escape'):
            return command.escape()
        # If it is a connection object - use the cursor's escape
        elif isinstance(command, SQLConnection):
            return command.cursor.escape()
        elif isinstance(command, SQLDialect):
            interface = command.registry['interface']
            return interface.escape(command)
        else:
            raise SQLError("Cannot escape string, unless "
                "SQLConnection/SQLInterface provided.")
            
    else: 
        
    
    if isinstance(command, SQLCommand):
        
    
    if isinstance(command, basestring):
        if isinstance(sqlobj, SQLDialect):
            return sqlobj.registry['interface'].escape(command)
        else:
            raise SQLError("Cannot escape string")
    
    
    if isinstance(obj, SQLCommand):
        return obj.cursor.escape(obj)
    elif isinstance(obj, basestring):
        if hasattr(cursor, 'escape'):
            return dialect.escape(obj)
        elif hasattr(cursor, 'escape_string'):
            return connection.escape(obj)
        else:
            raise TypeError("connection does not have an escape or escape_string function")
    else:
        raise TypeError("'obj' should be a basestring or SQLCommand object.")
    
def execute(query, params=None):
    rich_core.AssertKlass(sqlcommand, SQLQuery, name='query')
    return sqlcommand.execute(params)

def results(sqlcommand, params=None):
    rich_core.AssertKlass(sqlcommand, SQLCommand, name='sqlcommand')
    return sqlcommand.results(params)

def run(sqlcommand, params=None):
    rich_core.AssertKlass(sqlcommand, SQLCommand, name='sqlcommand')
    return sqlcommand.run(params)

    
