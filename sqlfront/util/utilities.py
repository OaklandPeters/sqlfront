import json
import collections
import os

from sqlfront.extern import rich_core

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