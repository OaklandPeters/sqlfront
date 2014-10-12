from __future__ import absolute_import
import inspect
import collections

__all__ = ['VProperty', 'FProperty', 'SProperty']


class SProperty(property):
    """Very simple version of the class-based property object.
    Defers all operation to the built-in property function.
    """
    def __new__(cls, *args, **kwargs):
        return cls.__call__(*args, **kwargs)
    @classmethod
    def __call__(cls, *args, **kwargs):
        return cls._dispatch(*args, **kwargs)
    @classmethod
    def _dispatch(cls, *fargs, **fkwargs):
        if len(fargs)==1 and len(fkwargs)==0:
            if inspect.isclass(fargs[0]):
                return cls.from_class(fargs[0])
        return property(*fargs, **fkwargs)
    @classmethod
    def from_class(cls, klass):
        return property(*cls._validate_class(klass))
    @classmethod
    def _validate_class(cls, klass):     
        kdict = vars(klass)        
        fget = getitem(kdict, '_get', 'getter', 'fget', default=None)
        fset = getitem(kdict, '_set', 'setter', 'fset', default=None)
        fdel = getitem(kdict, '_del', 'deleter', 'fdel', default=None)
        doc = getitem(kdict, 'doc', default=None)
        if doc is None and fget is not None:
            doc = fget.__doc__
        return fget, fset, fdel, doc


def getitem(mapping, *aliases, **kwargs):
    for key in aliases:
        if key in mapping:
            return mapping[key]
    if 'default' in kwargs:
        return kwargs['default']
    else:
        raise KeyError('Keys not found: '+', '.join(aliases))



class VProperty(object):
    """Enchanced Python property, supporting 
    
    @TODO: Allow the function names for the class to be specified as
        either 'fget'/'getter', 'fset'/'setter', 'fdel'/'deleter', 'fval'/'validator'
    @TODO: Allow additional methods to be provided on a decorated class. Essentially
        anything not causing a conflict. basically I would like the class defined in
        the decorator to be in the method-resolution order for the new vproperty descriptor.
        (* complication: need to rename getter/setter/deleter/validator to fget/fset etc)
    @TODO: Consider having the names on the class be:
        '_get', '_set', '_del', '_validate' - so that pylint doesn't complain about them.
    
    """
    def __init__(self, *fargs, **fkwargs):
        """Check if used as a decorator for a class, or if used
        conventionally.
        """
        arguments = self.validate(*fargs, **fkwargs)
            
        (self.fget,
         self.fset,
         self.fdel,
         self.fval,
         self.__doc__) = arguments
         
    def validate(self, *fargs, **fkwargs):
        fget, fset, fdel, fval, doc = self._validate_dispatch(*fargs, **fkwargs)
        if doc is None and fget is not None:
            doc = fget.__doc__
        return fget, fset, fdel, fval, doc

        
    def _validate_dispatch(self, *fargs, **fkwargs):
        if len(fargs)==1 and len(fkwargs)==0:
            if inspect.isclass(fargs[0]):
                return self._validate_from_class(fargs[0])
        return self._validate_from_args(*fargs, **fkwargs)
    def _validate_from_args(self, fget=None, fset=None, fdel=None, fval=None, doc=None):
        """This is basically a validation function. Consider renaming?"""
        if doc is None and fget is not None:
            doc = fget.__doc__
        return fget, fset, fdel, fval, doc
    def _validate_from_class(self, klass):
        kdict = vars(klass)
        fget = getitem(kdict, 'fget', '_get', 'getter', default=None)
        fset = getitem(kdict, 'fset', '_set', 'setter', default=None)
        fdel = getitem(kdict, 'fdel', '_del', 'deleter', default=None)
        fval = getitem(kdict, 'fval', '_val', 'validator', default=None)
        doc  = getitem(kdict, '__doc__', default=None)
        return fget, fset, fdel, fval, doc
    #----- Descriptors
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        return self.fget(obj)
    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        if self.fval is not None: #Validate, if possible
            value = self.fval(obj, value)
        self.fset(obj, value)
    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(obj)
    #----- Decorators
    def getter(self, fget):
        return type(self)(fget, self.fset, self.fdel, self.fval, self.__doc__)
    def setter(self, fset):
        return type(self)(self.fget, fset, self.fdel, self.fval, self.__doc__)
    def deleter(self, fdel):
        return type(self)(self.fget, self.fset, fdel, self.fval, self.__doc__)
    def validator(self, fval):
        return type(self)(self.fget, self.fset, self.fdel, fval, self.__doc__)


class FProperty(object):
    """Enhanced class-based property."""
    def __init__(self, *fargs, **fkwargs):
        """
        """
        arguments = self.validate(*fargs, **fkwargs)
            
        (self.fget,
         self.fset,
         self.fdel,
         self.fval,
         self.__doc__) = arguments
         

    #----- Descriptors
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        return self.fget(obj)        
    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        if self.fval is not None: #Validate, if possible
            value = self.fval(obj, value)
        self.fset(obj, value)
    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(obj)
    #----- Decorators
    def getter(self, fget):
        return type(self)(fget, self.fset, self.fdel, self.fval, self.__doc__)
    def setter(self, fset):
        return type(self)(self.fget, fset, self.fdel, self.fval, self.__doc__)
    def deleter(self, fdel):
        return type(self)(self.fget, self.fset, fdel, self.fval, self.__doc__)
    def validator(self, fval):
        return type(self)(self.fget, self.fset, self.fdel, fval, self.__doc__)
    
    #------ Input Validation
    # ... probably unnecssarily complicated
    def validate(self, *fargs, **fkwargs):
        """Dispatch. Check if used as a decorator for a class, or if used
        conventionally, then validate inputs.
        """
        fget, fset, fdel, fval, doc = self._validate_dispatch(*fargs, **fkwargs)
        if doc is None and fget is not None:
            doc = fget.__doc__
        self._validate_typecheck(fget, fset, fdel, fval, doc)
        return fget, fset, fdel, fval, doc
        
    def _validate_dispatch(self, *fargs, **fkwargs):
        if len(fargs)==1 and len(fkwargs)==0:
            if inspect.isclass(fargs[0]):
                return self._validate_from_class(fargs[0])
        return self._validate_from_args(*fargs, **fkwargs)
    
    def _validate_from_args(self, fget=None, fset=None, fdel=None, fval=None, doc=None):
        """This is basically a validation function. Consider renaming?"""
        if doc is None and fget is not None:
            doc = fget.__doc__
        return fget, fset, fdel, fval, doc

    def _validate_from_class(self, klass):
        kdict = vars(klass)
        fget = getitem(kdict, 'fget', '_get', 'getter', default=None)
        fset = getitem(kdict, 'fset', '_set', 'setter', default=None)
        fdel = getitem(kdict, 'fdel', '_del', 'deleter', default=None)
        fval = getitem(kdict, 'fval', '_val', 'validator', default=None)
        doc  = getitem(kdict, '__doc__', default=None)

        if doc is None and fget is not None:
            doc = fget.__doc__
        return fget, fset, fdel, fval, doc
    
    def _validate_typecheck(self, fget, fset, fdel, fval, doc):
        fget = self._validate_typecheck_func(fget, 'fget')
        fset = self._validate_typecheck_func(fset, 'fset')
        fdel = self._validate_typecheck_func(fdel, 'fdel')
        fval = self._validate_typecheck_func(fval, 'fval')
        if not isinstance(doc, (basestring, type(None))):
            raise TypeError("'doc' must be basestring or NoneType")
        
    def _validate_typecheck_func(self, farg, name):
        if not isinstance(farg, (collections.Callable, type(None))):
            raise TypeError("'{0}' must be Callable or NoneType.".format(name))
        return farg
            


