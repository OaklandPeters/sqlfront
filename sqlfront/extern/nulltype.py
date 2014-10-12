import abc
import types
import collections



__all__ = ['NullType', 'NotPassed', 'NotPassedType', 'Optionable']

class NullType(object):
    """Superclass of NoneType, NotPassed, and optional."""
    __metaclass__ = abc.ABCMeta
NullType.register(types.NoneType)

class NotPassedType(NullType):
    """Represents non-passed arguments. Alternative to using None, useful
    in cases where you want to distinguish passing in the value of 'None' from
    'No-value-was-provided'."""
    def __init__(self):
        pass
NotPassed = NotPassedType()

class Optionable(NotPassedType):
    """Abstract base class for Option-like classes which define their
    own deoption() method.
    """
    @abc.abstractmethod
    def deoption(self):
        pass
    @classmethod
    def __subclasshook__(cls, subklass):
        if cls is Optionable:
            if _hasattr(subklass, 'deoption'):
                return True
        return NotImplemented



#==============================================================================
#        Local Utility Functions
#==============================================================================
def _hasattr(subklass, attr):
    """Determine if subklass, or any ancestor class, has an attribute.
    Copied shamelessly from the abc portion of collections.py.
    """
    try:
        return any(attr in B.__dict__ for B in subklass.__mro__)
    except AttributeError:
        # Old-style class
        return hasattr(subklass, attr)