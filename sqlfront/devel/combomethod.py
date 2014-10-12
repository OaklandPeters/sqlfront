import functools
import types

class variant(object):
    def __init__(self, func):
        self.func = func
        if hasattr(func, '__name__'):
            self.name = func.__name__
        else:
            self.name = repr(func)

    def __get__(self, obj, objtype=None):
        if obj is None: #classmethod
            #return functools.partial(self.func, objtype)
            return types.MethodType(self.func, objtype)
        else:  #instancemthod
            return types.MethodType(self.func, obj)
            #return functools.partial(self.func, obj)
            




class MyClass(object):
    def __init__(self):
        pass
    @variant
    #@classmethod
    def variant(self, first):
        print(self, first)
        print()
        return "self: {0}, first: {1}".format(self, first)

inst = MyClass()

print(MyClass.variant('foo'))
print(inst.variant('bar'))

inst.variant = 'things'

print(inst.variant)
print()