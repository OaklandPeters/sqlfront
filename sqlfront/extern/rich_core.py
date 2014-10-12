"""
Functions from rich_X.py modules, which are used by other rich_X.py modules.
Moved here, so rich_X.py modules do NOT import each other -- preventing
circular dependencies.

This modules is not intended to be used by anything other than building
the rich_X.py modules.


@TODO Write unit-tests for this.

@TODO the category-functor code is too large and elaborate at this point
    see if I can cut it down to just the AssertKlass/IsKlass part
@TODO consider removing or greater reducing size of doctests for the
    Assert/Validation code. --> rich_core_test.py
@TODO for Associative - consider making it require __iter__
    so that Associative can Mixin/interact with pairs(),indexes(),elements()
@TODO this file is getting too large. Consider removing parts, or repacking
    it into smaller units.
@TODO pairs(), elements(), indexes(): ammend so that they apply exactly 
    to objects which match the Associative ABC.
    ... currently, pairs/elements/indexes only works for NonString
    Mappings and Sequences,
    but Associative is defined for any iterable with __getitem__
    ... perhaps: they should do:
    AssertKlass(container,Associative):
    if _hasattr(container,'keys'):    #~Mappings
        gen = ((key,container[key]) for key in container.keys())
    else:    #~Iterables
        gen = enumerate(container)
@TODO Associative(): also ammend so it closely matches conditions for the
    pairs(), elements(), indexes()
"""

import collections
import abc
import functools



#--------------------------------------------------------------------
#    Local Utility
#--------------------------------------------------------------------
def _inside(obj,container):
    """Used by IsEnum()/AssertEnum()"""
    return (obj in container)
def _haskey(mapping,key):
    """Used by HasKeys()/AssertKeys()
    #    requires mapping is Mapping, and key is hashable"""
    return (key in mapping)



#--------------------------------------------------------------------
#    Core Functions
#--------------------------------------------------------------------
# Used frequently by other rich_X modules.
def _hasattr(subklass, attr):
    """Determine if subklass, or any ancestor class, has an attribute.
    Copied shamelessly from the abc portion of collections.py.
    """
    try:
        return any(attr in B.__dict__ for B in subklass.__mro__)
    except AttributeError:
        # Old-style class
        return hasattr(subklass, attr)

def required(mapping, keys):
    """Throws error if mapping does not have all of keys."""
    assert(isinstance(mapping,collections.Mapping)), "Not a mapping."
    for key in keys:
        if key not in mapping:
            raise KeyError(key)
def defaults(*mappings):
    """Handles defaults for sequence of mappings (~dicts).
    The first (left-most) mapping is the highest priority."""
    return dict(
        (k, v)
        for mapping in reversed(mappings)
        for k, v in mapping.items()
    )
    #Old form of defaults. Less efficient
#     basis = {}
#     for mapping in mappings:
#         #basis.update(mapping)
#
#         for key in mapping:
#             if key not in basis:
#                 basis[key] = mapping[key]
#
#     return basis


class ClassProperty(property):
    """Provides a getter-property for classmethods. Due to complicated reasons,
    there is no way to make classmethod setter-properties work in Python

    >>> class MyClass(object):
    ...     @ClassProperty
    ...     @classmethod
    ...     def mymethod(cls):
    ...         return 'data'
    >>> MyClass.mymethod
    'data'
    """
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()

#NonStringIterable belongs to rich_type.py
class NonStringIterable(object):
    '''Provides an ABC to duck-type check for iterables OTHER THAN strings.
    Includes Sequences (lists, tuples), Mappings (dicts), and Iterators but not
    strings (unicode or str).

    >>> issubclass(int, NonStringIterable)
    False
    >>> issubclass(list, NonStringIterable)
    True
    >>> issubclass(str, NonStringIterable)
    False
    >>> isinstance(1, NonStringIterable)
    False
    >>> isinstance(["a"], NonStringIterable)
    True
    >>> isinstance("a", NonStringIterable)
    False
    >>> isinstance(unicode('abc'), NonStringIterable)
    False
    >>> isinstance(iter("a"), NonStringIterable)
    True
    '''
    __metaclass__ = abc.ABCMeta
    __slots__ = ()
    @abc.abstractmethod
    def __iter__(self):
        while False:
            yield None
    @classmethod
    def __subclasshook__(cls, subklass):
        if cls is NonStringIterable:
            #if any("__iter__" in B.__dict__ for B in subklass.__mro__):
            if _hasattr(subklass, "__iter__"):
                return True
        return NotImplemented


class NonStringSequence(collections.Sized, collections.Iterable, 
    collections.Container):
    '''Convenient ABC to duck-type check for sequences OTHER THAN strings.
    Includes Sequences (lists, tuples) but not strings (unicode or str), 
    Mappings (dicts), or Iterators.

    >>> issubclass(int,NonStringSequence)
    False
    >>> issubclass(list,NonStringSequence)
    True
    >>> isinstance(1,NonStringSequence)
    False
    >>> isinstance(["a"],NonStringSequence)
    True
    >>> isinstance("a",NonStringSequence)
    False
    >>> isinstance(unicode('abc'),NonStringSequence)
    False
    >>> isinstance(iter("a"),NonStringSequence)
    False
    '''
    __metaclass__ = abc.ABCMeta
    @classmethod    
    def __subclasshook__(cls, subklass):
        if cls is NonStringSequence:
            if (issubclass(subklass, collections.Sequence)
                and not issubclass(subklass,basestring)):
                return True
        return NotImplemented

    @abc.abstractmethod
    def __getitem__(self, index):
        raise IndexError

    def __iter__(self):
        i = 0
        try:
            while True:
                val = self[i]
                yield val
                i += 1
        except IndexError:
            return
    def __contains__(self, value):
        for val in self:
            if val == value:
                return True
        return False
    def __reversed__(self):
        for i in reversed(range(len(self))):
            yield self[i]
    def index(self, value):
        """Return index of first element matching 'value'."""
        for ind, val in enumerate(self):
            if val == value:
                return ind
        raise ValueError
    def count(self, value):
        """Count instances of value."""
        return sum(1 for v in self if v == value)
NonStringSequence.register(tuple)
NonStringSequence.register(xrange)


class Associative(object): #pylint: disable=abstract-class-not-used, incomplete-protocol
    '''Abstract Base Class for objects which are Iterable, and respond to
    item-retreival (__getitem__).
    Includes Mappings and Sequences, but not Iterators or strings (strings
    intentionally excluded).

    Importantly, this indicates objects on which the generic iterator functions
        pairs(),elements(),indexes() can operate.
    @TODO ammend pairs/elements/indexes() so that this is actually true.
    @TODO also ammend Associative so this is true.
        ... currently, pairs/elements/indexes only works for NonString
        Mappings and Sequences,
        but Associative is defined for any iterable with __getitem__
    ... perhaps: they should do one of two:

        AssertKlass(container,Associative):
        if HasAttr(container,'keys'):    #~Mappings
            gen = ((key,container[key]) for key in container.keys())
        else:    #~Iterables
            gen = enumerate(container)

    >>> isinstance({},Associative)
    True
    >>> isinstance([],Associative)
    True
    >>> isinstance("",Associative)
    False
    >>> issubclass(int,Associative)
    False
    >>> from collections import defaultdict
    >>> issubclass(defaultdict,Associative)
    True
    '''
    __metaclass__ = abc.ABCMeta
    __slots__ = ()
    @abc.abstractmethod
    def __iter__(self):
        while False:
            yield None
    @abc.abstractmethod
    def __getitem__(self, key):
        raise KeyError
    @classmethod
    def __subclasshook__(cls, subklass):
        if cls is Associative:            
            #'has': simple syntactic sugar
            _has = lambda name: _hasattr(subklass,name)
            if _has("__getitem__") and _has("__iter__"):
                return True
        return NotImplemented

#==============================================================================
#        BASIC Iterator Tools - widely used
#==============================================================================

#pairs/indexes/elements ~~ items/keys/values , but for sequences and mappings
#These correspond to iteration over objects which are Associative (see class).
def pairs(container, iterator=False):
    '''.items()-like iterator function, generalized for Sequence and Mappings,
    while not iterating over strings.

    ?? Question: for non-Sequence, non-Mapping 'container', should this:
        (1) raise TypeError, or (2) return iter([]) for
    '''
    if isinstance(container, collections.Mapping):
        #Not all Mappings have an iteritems method.
        gen = collections.Mapping.iteritems(container)


    elif (isinstance(container, collections.Sequence)
        and not isinstance(container, basestring)):
    #@todo:
    #elif IsKlass(container,Sequence,notklasses=basestring):
        gen = enumerate(container)
    else:
        raise TypeError("Cannot build a pairs() iterator because '{0}' object"
            " is either not a Mapping or a Sequence, or is a basestring."
            .format(type(container)))

    if iterator:
        return gen
    else:
        return list(gen)

def indexes(container, iterator=False):
    """Return keys or numeric indexes (if a sequence)."""
    gen = (index for index, element in pairs(container, iterator=True))

    if iterator:
        return gen
    else:
        return list(gen)

def elements(container, iterator=False):
    """Returns all values from mappings, and all elements of sequences."""
    gen = (element for index, element in pairs(container, iterator=True))

    if iterator:
        return gen
    else:
        return list(gen)

def ensure_tuple(obj):
    """Ensure that object is wrapped in a tuple. Handles some special casees.
    tuples are unchanged; NonStringSequences and Iterators are converted into
    a tuple containing the same elements; all others are wrapped by a tuple.

    (~iterable, non-mutable sequence).
    Also works similar to ensure(NonStringIterable).

    >>> ensure_tuple(['a','b'])
    ('a', 'b')
    >>> ensure_tuple('abc')
    ('abc',)
    >>> ensure_tuple(iter(range(4)))
    (0, 1, 2, 3)
    >>> ensure_tuple(None)
    (None,)
    >>> ensure_tuple({'a':1, 'b':2})
    ({'a': 1, 'b': 2},)
    """
    _is = lambda klass: isinstance(obj,klass)
    if _is(tuple):
        return obj
    #Sequences
    #Iterators & Generators - consume into a tuple
    elif _is(NonStringSequence) or _is(collections.Iterator):
        return tuple(obj)
    #Other Iterables
    #Strings, and non-iterables -- wrap in an iterable first
    else:
        return tuple([obj])


class abstractclassmethod(classmethod): #pylint: disable=invalid-name
    """A decorator indicating abstract classmethods, similar to abstractmethod.
    Requires that the class descend from abc.ABCMeta.
    This is a backport of the abstract-class-method from Python 3.2 to Python 2.6.
    """
    __isabstractmethod__ = True

    def __init__(self, a_callable):
        #assert(issubclass(callable, abc.ABCMeta)), "object is not a subclass of ABCMeta."
        #assert(callable(a_callable)), "object is not callable."
        a_callable.__isabstractmethod__ = True
        super(type(self), self).__init__(a_callable) #pylint: disable=bad-super-call


#==============================================================================
#        Type Checking, Validation, and Assertion
#==============================================================================
#Core functions occur in triplets: (1) Is/Has, (2) Assert, (3) Validate
#For a particular PredicateFunctor - defined by a single function
#
#(1) IsType/AssertType/ValidateType
#        the most commonly used. checks isinstance()
#(2) IsSubclass/AssertSubclass/ValidateSubclass
#        rarely used, but very similar to IsType. Checks issubclass()
#(3) HasAttrs
#        Underlyies the core concept of duck-typing.
#(4) HasKeys
#(5) IsEnum
#
def category_message(obj,pos=None,neg=None,name=None,namefunc=None,verb=None):
    """
    category_message(obj,
        pos         = cls.handler(pos),
        neg         = cls.handler(neg),
        namefunc    = cls.category_name,
        verb        = "be in",
    )
    """
    if verb == None:
        verb = "satisfies categories "
    if not callable(namefunc):
        namefunc = lambda category: str(category)[:40]

    msg = str.format(
        "{0} of type '{1}' should",
        "'"+name+"'" if (isinstance(name,basestring)) else 'Object',
        type(obj).__name__
    )
    if pos != None:
        msg += " {verb} {categories}".format(
            verb = verb,
            categories = map(namefunc,pos),
        )
    if neg != None:
        if pos != None:
            msg += " and"
        msg += " not {verb} {categories}".format(
            verb = verb,
            categories = map(namefunc,neg),
        )
    return msg
#-----------------   Ancestor Abstract Base Classes   -----------------
class IsCategoryABC(object):
    """
    @todo: replace .reducer() with .pos_reducer(),.neg_reducer()
        So their name can be used in message() -->
            be instance of {reducer.__name__} {group}
            --> be instance of any (Sequence, NoneType)
    def __new__(cls,obj,pos=None,neg=None):
        obj_pos = cls.pos_reducer(cls.mapper(obj,pos)) if (pos!=None) else True
        obj_pos = True  if (pos==None) else cls.pos_reducer(cls.mapper(obj,pos))
        obj_neg = cls.neg_reducer(cls.mapper(obj,neg)) if (neg!=None) else False
        obj_neg = False if (neg==None) else cls.neg_reducer(cls.mapper(obj,neg))
        return (obj_pos and not obj_neg)
    """
    __metaclass__ = abc.ABCMeta
    def __new__(cls,obj,pos=None,neg=None):
        obj_pos = cls.reducer(cls.mapper(obj,pos)) if (pos!=None) else True
        obj_neg = cls.reducer(cls.mapper(obj,neg)) if (neg!=None) else False
        #obj_pos = cls.mapper(obj,pos) if (pos != None) else True
        #obj_neg = cls.mapper(obj,neg) if (neg != None) else False

        return (obj_pos and not obj_neg)
    #------ Abstract Functions
#     definition = abc.abstractproperty(lambda self: NotImplemented)
#     meets = abc.abstractmethod(lambda self, category: NotImplemented)
#     predicate = abc.abstractmethod(lambda self, obj, category: NotImplemented)
    @abc.abstractproperty
    def definition(self):
        return NotImplemented
    @abc.abstractproperty
    def meets(cls, category):
        return NotImplemented
    @abc.abstractproperty
    def predicate(cls, obj, category):
        return NotImplemented
    #-------- Mixin Methods
    #reducer = all
    @classmethod
    def reducer(cls, sequence):
        """Reduce a sequence to a single value.
        Nearly always 'all' or 'any'."""
        return all(sequence)
    #-------- Strategy Functions
    @classmethod
    def mapper(cls, obj, group):
        """Map predicate onto group of categories, for a given object."""
        return [
            cls.predicate(obj, category) #pylint: disable=no-value-for-parameter
            for category in cls.handler(group)
        ]
    @classmethod
    def handler(cls, group):
        if group == None:
            #group: no categories provided
            return group
        elif isinstance(group,NonStringSequence):
            #group: a sequence of categories
            for category in group:
                #cls.meets(category)
                cls.confirm(category)
            return tuple(group)
        else:
            #group: a single category
            cls.meets(group) #pylint: disable=no-value-for-parameter
            return tuple([group])

class AssertCategoryABC(object):
    """
    Intended to inherit from an instance of IsCategoryABC. Ex:
    class AssertType(AssertCategoryABC,IsType):
        ...
    """

    __metaclass__ = abc.ABCMeta
    def __new__(cls,obj,pos=None,neg=None,msg=None,name=None):
        if not cls.checker(obj,pos,neg):
            if msg == None:
                msg = cls.message(obj, pos=pos, neg=neg, name=name) #pylint: disable=no-value-for-parameter
            raise cls.exception(msg)
        else:
            return obj
    #-------    
    @abc.abstractmethod
    def checker(cls, obj, pos=None, neg=None):
        """Usually a related class, descended from IsCategoryABC()."""
        return NotImplemented
    @abc.abstractmethod
    def message(cls, obj, pos=None, neg=None, name=None):
        return NotImplemented    
    @abc.abstractmethod
    def exception(cls):
        return NotImplemented

class ValidateCategoryABC(object):
    """Sugar. Partial for filling in arguments other than obj 
    to AssertCategoryABC."""
    __metaclass__ = abc.ABCMeta
    @abc.abstractproperty
    def asserter(self):
        return NotImplemented
    def __new__(cls,*args,**kwargs):
        @functools.wraps(cls.asserter)
        def wrapped(obj):
            return cls.asserter(obj, *args, **kwargs) #pylint: disable=star-args
        return wrapped

class PredicateFunctor(object):
    """
    PredicateFunctor():
        Gives:     confirm(), .name
        Requires:  .meets(), .predicate(), .definition
    """
    __metaclass__ = abc.ABCMeta
    #-------- Mixin
    @classmethod
    def confirm(cls,category):
        if not cls.meets(category):
            raise TypeError(str.format(
                "Object of type {0} is not a valid category for {1}.",
                type(category).__name__,cls.__name__
            ))
        return category
    @classmethod
    def predicate(cls, obj, category):
        return cls.definition(obj, category)
    #-------- Abstract Properties
    @abc.abstractmethod
    def meets(self,category):
        return NotImplemented
    @abc.abstractproperty
    def definition(self):
        return NotImplemented
    @abc.abstractmethod
    def category_name(self,category):
        return NotImplemented


#-----------------   Instanced Predicate Functors   -----------------
class IsInstanceFunctor(PredicateFunctor):
    definition = staticmethod(isinstance)
    @classmethod
    def meets(cls,category):
        return isinstance(category,type)
    @classmethod
    def category_name(cls,category):
        return category.__name__

class HasAttrsFunctor(PredicateFunctor):
    definition = staticmethod(_hasattr)
    @classmethod
    def meets(cls,category):
        return isinstance(category,basestring)
    @classmethod
    def category_name(cls,category):
        return category

class IsEnumFunctor(PredicateFunctor):
    definition = staticmethod(_inside)
    @classmethod
    def meets(cls,category):
        return isinstance(category,NonStringSequence)
    @classmethod
    def category_name(cls,category):
        try:
            return category.__name__
        except AttributeError:
            try:
                return category.name
            except AttributeError:
                try:
                    assert(len(str(category)) < 80)
                    return str(category)
                except (AttributeError, AssertionError):
                    return str(category)[:80]+"..."

class IsSubclassFunctor(PredicateFunctor):
    definition = staticmethod(issubclass)
    @classmethod
    def meets(cls,category):
        return isinstance(category, type)
    @classmethod
    def category_name(cls,category):
        return category.__name__

class HasKeysFunctor(PredicateFunctor):
    #category is a key
    definition = staticmethod(_haskey)
    @classmethod
    def meets(cls, category):
        return isinstance(category, collections.Hashable)
    @classmethod
    def category_name(cls, category):
        #category is a key
        return str(category)


#-----------------   isinstance Category Predicates   -----------------
class IsType(IsInstanceFunctor,IsCategoryABC):
    """
    IsType(obj,pos=None,neg=None) -> bool
    -----
    @future: use UniversalSet/UniversalClass and EmptySet/Nil
        as default values.

    >>> IsType({},dict)
    True
    >>> IsType({},type(None))
    False
    >>> obj = object()
    >>> IsType(obj,pos=object,neg=type(None))
    True
    >>> IsType(None,pos=(object,),neg=type(None))
    False

    >>> IsType('mystr',[basestring,type(None)],[int,unicode])
    True
    >>> IsType(None,[type(None),int],neg=(basestring,))
    True

    >>> IsType((1,2,3),basestring)
    False
    >>> IsType((1,2,3),(collections.Sequence,type(None)))
    True
    >>> IsType((1,2,3),(collections.Sequence,type(None)),tuple)
    False
    >>> IsType("asda",str)
    True
    >>> IsType(unicode("asda"),basestring,str)
    True
    >>> IsType("asda",basestring,str)
    False
    >>> IsType(['a',1,'b'],NonStringIterable)
    True
    >>> IsType('a1b',NonStringIterable)
    False

    >>> IsType('aa','akakl')
    Traceback (most recent call last):
    TypeError: isinstance() arg 2 must be a class, type, or tuple of classes and types
    """
    reducer = any
#older code uses the name 'IsKlass' instead of 'IsType'
IsKlass = IsType

class AssertType(AssertCategoryABC,IsType):
    """
    >>> AssertType({},object)
    {}
    >>> AssertType("aa",pos=collections.Sequence,neg=basestring,name='nameless')
    Traceback (most recent call last):
    TypeError: 'nameless' of type 'str' should be instance of ['Sequence'] and not be instance of ['basestring']

    >>> AssertType({},collections.Sequence)
    Traceback (most recent call last):
    TypeError: Object of type 'dict' should be instance of ['Sequence']
    >>> AssertType({'a':1},collections.Mapping)
    {'a': 1}
    >>> AssertType([1,2,'a'],list)
    [1, 2, 'a']
    >>> AssertType([1,2,'a'],collections.Sequence)
    [1, 2, 'a']
    >>> AssertType([],(collections.Sequence,list),(type,type(None)))
    []
    >>> AssertType([],pos=(collections.Sequence,list),neg=(type,type(None),object))
    Traceback (most recent call last):
    TypeError: Object of type 'list' should be instance of ['Sequence', 'list'] and not be instance of ['type', 'NoneType', 'object']

    """
    checker = IsType
    exception = TypeError
    @classmethod
    def message(cls,obj,pos=None,neg=None,name=None):
        return category_message(obj,
            pos     = cls.handler(pos),
            neg     = cls.handler(neg),
            name    = name,
            namefunc= cls.category_name,
            verb    = "be instance of",
        )
#older code uses the name 'AssertKlass' instead of 'AssertType'
AssertKlass = AssertType

class ValidateType(ValidateCategoryABC):
    asserter = AssertType


#-----------------   hasattr() Category Predicates   -----------------

class HasAttrs(HasAttrsFunctor,IsCategoryABC):
    """
    >>> HasAttrs({},("__contains__","values"))
    True
    >>> HasAttrs([],("__contains__","values"))
    False
    >>> class MyClass(object):
    ...     def budget(self): return 'foo'
    ...     def record(self): return 'bar'
    >>> HasAttrs(MyClass,'budget')
    True
    >>> HasAttrs(MyClass,'payroll')
    False
    >>> HasAttrs(MyClass,'payroll',('user','record'))
    False
    >>> HasAttrs(MyClass,'budget',neg=('user','record'))
    False
    """
    def __new__(cls,obj,pos=None,neg=None):
        obj_pos = all(cls.mapper(obj,pos)) if (pos!=None) else True
        obj_neg = any(cls.mapper(obj,neg)) if (neg!=None) else False

        return (obj_pos and not obj_neg)

class AssertAttrs(AssertCategoryABC,HasAttrs):
    """
    >>> AssertAttrs({},("__contains__","values"))
    {}
    >>> AssertAttrs([],("__contains__","values"))
    Traceback (most recent call last):
    AttributeError: Object of type 'list' should have attributes ['__contains__', 'values']
    >>> class MyClass(object):
    ...     def budget(self): return 'foo'
    ...     def record(self): return 'bar'
    >>> AssertAttrs(MyClass,'budget')
    <class '__main__.MyClass'>
    >>> AssertAttrs(MyClass,'payroll')
    Traceback (most recent call last):
    AttributeError: Object of type 'type' should have attributes ['payroll']
    >>> AssertAttrs(MyClass,'payroll',('user','record'))
    Traceback (most recent call last):
    AttributeError: Object of type 'type' should have attributes ['payroll'] and not have attributes ['user', 'record']
    """
    checker     = HasAttrs
    exception   = AttributeError
    @classmethod
    def message(cls,obj,pos=None,neg=None,name=None):
        return category_message(obj,
            pos     = cls.handler(pos),
            neg     = cls.handler(neg),
            name    = name,
            namefunc= cls.category_name,
            verb    = "have attributes",
        )


#-----------------   enum Category Predicates   -----------------
#    ~
class IsEnum(IsEnumFunctor,IsCategoryABC):
    """
    Is obj drawn from finite list of possibilities, and not from another.
    >>> IsEnum('string',('string','text',None))
    True
    >>> IsEnum('string',('string','text',None),'string')
    False
    >>> IsEnum(12,('string','text',None))
    False
    >>> IsEnum(123,('string','text',None))
    False
    >>> IsEnum(45,45)
    True
    >>> IsEnum('aa','aa')
    True
    >>> IsEnum('aa',('aa',))
    True
    """
    reducer = any
    @classmethod
    def handler(cls,group):
        wrap = lambda cat: tuple(cat) if cls.meets(cat) else tuple([cat])        
        if group == None:
            #enum group: no categories provided
            return group
        #elif isinstance(group,NonStringSequence):
        elif cls.meets(group):
            #Two possible enum groups:
            #1: a sequence of enum categories
            #  NonStringSequence containing at least one NonStringSequence
            #    ex. [['a','b'],'c'] --> (('a','b'),('c',))
            #        [['a','b']] --> (('a','b'),)
            if any(cls.meets(category) for category in group):
                return tuple([wrap(category) for category in group])
            #2: a single category, which is a sequence
            #  whether: ['a','b']-->(('a','b'),)
            else:
                return tuple([wrap(group)])
        else:
            #enum group: single atom: 'a' --> ('a',)
            return tuple([wrap(group)])


class AssertEnum(AssertCategoryABC,IsEnum):
    """
    >>> AssertEnum('string',('string','text',None))
    'string'
    >>> AssertEnum('string',('string','text',None),'string')
    Traceback (most recent call last):
    ValueError: Object of type 'str' should be in ["('string', 'text', None)"] and not be in ["('string',)"]
    >>> AssertEnum(123,('string','text',None))
    Traceback (most recent call last):
    ValueError: Object of type 'int' should be in ["('string', 'text', None)"]
    >>> AssertEnum(123,('string','text',None),(123,34))
    Traceback (most recent call last):
    ValueError: Object of type 'int' should be in ["('string', 'text', None)"] and not be in ['(123, 34)']
    >>> AssertEnum(45,45)
    45
    """
    checker = IsEnum
    exception = ValueError
    @classmethod
    def message(cls,obj,pos=None,neg=None,name=None):
        return category_message(obj,
            pos     = cls.handler(pos),
            neg     = cls.handler(neg),
            name    = name,
            namefunc= cls.category_name,
            verb    = "be in",
        )


#-----------------   issubclass() Category Predicates   -----------------
class IsSubclass(IsSubclassFunctor,IsCategoryABC):
    """IsSubklass(obj,isklasses=None,notklasses=None) -> bool
    -----
    @future: use UniversalSet/UniversalClass and EmptySet/Nil
        as default values.

    >>> IsSubclass(dict,pos=object,neg=type(None))
    True
    >>> IsSubclass(type(None),pos=object,neg=type(None))
    False
    >>> IsSubclass(str,[basestring,type(None)],[int,unicode])
    True
    >>> IsSubclass(type((1,2,3)),basestring)
    False
    >>> IsSubclass(type((1,2,3)),(collections.Sequence,type(None)))
    True
    >>> IsSubclass(type((1,2,3)),(collections.Sequence,type(None)),tuple)
    False

    >>> IsSubclass(list,NonStringIterable)
    True
    >>> IsSubclass(str,NonStringIterable)
    False
    """
    reducer = any

class AssertSubclass(AssertCategoryABC,IsSubclass):
    """
    >>> AssertSubclass(dict,collections.Sequence)
    Traceback (most recent call last):
    ValueError: Object of type 'type' should be subclass of ['Sequence']
    >>> AssertSubclass(dict,(object,type),(collections.Mapping))
    Traceback (most recent call last):
    ValueError: Object of type 'type' should be subclass of ['object', \
'type'] and not be subclass of ['Mapping']
    >>> AssertSubclass(dict,collections.Mapping)
    <type 'dict'>
    >>> AssertSubclass(list,collections.Sequence)
    <type 'list'>
    >>> AssertSubclass(NonStringSequence,collections.Iterable)
    <class '__main__.NonStringSequence'>
    >>> AssertSubclass(IsType,PredicateFunctor)
    <class '__main__.IsType'>
    """
    checker = IsSubclass
    exception = ValueError
    @classmethod
    def message(cls,obj,pos=None,neg=None,name=None):
        return category_message(obj,
            pos     = cls.handler(pos),
            neg     = cls.handler(neg),
            name    = name,
            namefunc= cls.category_name,
            verb    = "be subclass of",
        )

#-----------------   haskeys Category Predicates   -----------------

class HasKeys(HasKeysFunctor, IsCategoryABC):
    """
    >>> mydict = {'a':1, 'b':2, 32:3, (2,3,'a'):4}
    >>> HasKeys(mydict,'b')
    True
    >>> HasKeys(mydict,'c')
    False
    >>> HasKeys(mydict,['b',32,31])
    False
    >>> HasKeys(mydict,['b',32,(2,3,'a')])
    True
    >>> HasKeys(mydict,['b',32,31],neg=32)
    False
    >>> HasKeys(['a','b'],[0,1])
    False
    """
class AssertKeys(AssertCategoryABC, HasKeys):
    """
    >>> mydict = {'a':1,'b':2}
    >>> AssertKeys(mydict,['b','c'],name='My Dictionary')
    Traceback (most recent call last):
    KeyError: "'My Dictionary' of type 'dict' should have all of ['b', 'c']"
    >>> AssertKeys(mydict,'a')
    {'a': 1, 'b': 2}
    >>> AssertKeys({'a':1},'b')
    Traceback (most recent call last):
    KeyError: "Object of type 'dict' should have all of ['b']"
    """
    checker = HasKeys
    exception = KeyError
    @classmethod
    def message(cls,obj,pos=None,neg=None,name=None):
        return category_message(obj,
            pos     = cls.handler(pos),
            neg     = cls.handler(neg),
            name    = name,
            namefunc= cls.category_name,
            verb    = "have all of",
        )




if __name__ == "__main__":
    import doctest
    doctest.testmod()

    def doc_check(func):
        """Use to check specific functions, or get more information
        on why they failed the doctest."""
        doctest.run_docstring_examples(func,globals())
