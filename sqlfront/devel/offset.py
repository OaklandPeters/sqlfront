"""
Trick for selecting a group of records with an offset, within a large table.
MySQL (and maybe other SQL dialects) tend not to optimize for this. Hence,
if we force it to optimize using it's primary-key index, the query-time is
improved by several orders-of-magnitude (often > 1000x).


This is often called 'Late Row Lookup'
"""




def late_row_lookup(table, offset, count=None, pkey=None):
    table, offset, count, pkey = _validate_lrl(table, offset, count, pkey)
    
    template = "\n".join(
        "SELECT outerT.*",
        "    FROM (",
        "    SELECT {primary_key}",
        "    FROM {table}",
        "    ORDER BY {primary_key}",
        "    LIMIT {count}",
        "    OFFSET {offset}",
        ") as innerT",
        "JOIN {table} as outerT",
        "ON outerT.{primary_key} = innerT.{primary_key};",
    )
    
    return template.format(
        primary_key = pkey, table = table, offset = offset, count = count
    )

def _validate_lrl(table, offset, count=NotPassed, pkey=NotPassed):
    # Table
    if not isinstance(table, basestring):
        raise TypeError("'table' must be of type basestring.")
    # Offset
    offset = _validate_int_input(offset, 'offset')
    # Count
    count = _validate_int_input(count, 'count', default='100')
    # Primary Key
    if isinstance(pkey, type(None)):
        pkey = _get_primary_key(table) #Placeholder function
    
    return table, offset, count, pkey

class NullType(object):
    __metaclass__ = abc.ABCMeta
NullType.register(types.NoneType)

class NotPassed(NullType):
    pass

def _validate_int_input(value, var_name, default=NotPassed):
    """
    
    Assert.convertible(value, int, name=var_name)
    """
    if isinstance(value, basestring):
        try:
            int(value)
        except ValueError:
            raise ValueError(str.format(
                "'{0}' string must be convertible to an integer: '{1}'",
                _class_name(value), value
            ))
        return str(value)
    elif isinstance(value, int):
        return str(value)
    elif isinstance(value, NotPassed):
        if not isinstance(default, NotPassed):
            pass
        else:
            raise RunTimeError()
    else:
        raise TypeError(str.format(
            "'offset' should be type basestring or int, not '{0}'",
            offset.__class__.__name__
        ))

def _get_primary_key(table):
    """A placeholder function. It will actually come from the dialect (SQLDialect)
    object that late_row_lookup() is a part of (probably MySQLDialect). 
    """


class LateRowLookup(object):
    """Operator."""