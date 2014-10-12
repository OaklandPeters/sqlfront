from __future__ import absolute_import
import functools
import types

__all__ = ['NonBindingMethod']

class NonBindingMethod(object):
    """Acts like a static method when called from a class, and an instance
    method when called from an instance. In Python 2.
    This is base behavior in Python 3.
    
    This is also the behavior of methods on builtin types in Python 2.
    mystr.format(value) -->    calls str.format(mystr, value)
    """
    def __init__(self, func):
        self.func = func #Pure function object - not unbound method
        
    def __get__(self, obj, klass=None):
        if obj is None and klass is not None: #called from klass
            return self.func
        elif obj is not None and klass is not None: #called from object
            return types.MethodType(self.func, obj, klass)
            #this is loosely equivalent to:
            #return functools.partial(self.func, obj)
        else:
            raise TypeError("Unrecognized input combination.")