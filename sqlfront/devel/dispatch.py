import local_package.rich_core as rich_core

def escape(obj, cursor=None):
    """Return object as a string, with characters escaped.
    If connection provided, escapes as per that connection. Else uses default
    MySQL escaping."""
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
    
def execute(sqlcommand, params=None):
    rich_core.AssertKlass(sqlcommand, SQLCommand, name='sqlcommand')
    return sqlcommand.execute(params)

def results(sqlcommand, params=None):
    rich_core.AssertKlass(sqlcommand, SQLCommand, name='sqlcommand')
    return sqlcommand.results(params)

def run(sqlcommand, params=None):
    rich_core.AssertKlass(sqlcommand, SQLCommand, name='sqlcommand')
    return sqlcommand.run(params)

    
