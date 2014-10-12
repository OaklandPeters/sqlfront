from __future__ import absolute_import
import string
from .nonbindingmethod import NonBindingMethod

__all__ = ['StringTemplate']

class StringTemplate(str): #pylint: disable=too-many-public-methods
    """String - used for formatting statements. Unlike standard strings,
    it allows partial-appliction of formatting."""
    @NonBindingMethod
    def format(self, *args, **kwargs):
        """Convert args & kwargs to forms supporting partial-application,
        and invoke formatting operation (vformat).
        Returns type StringTemplate."""
        return StringTemplate(
            self.vformat(FormatList(args), FormatDict(kwargs))
        )
    @NonBindingMethod
    def vformat(self, fargs, fkwargs):
        """Invoke vformat from string, on self.
        Returns string, not StringTemplate."""
        return string.Formatter().vformat(self, fargs, fkwargs)

class FormatDict(dict):
    """Allows for 'partial' application of str.format()"""
    def __missing__(self, key):
        return "{" + key + "}"

class FormatList(list):
    def __getitem__(self, index):
        try:
            return super(FormatList, self).__getitem__(index)
        except IndexError:
            return self.__missing__(index)
    def __missing__(self, index):
        return "{" + str(index) + "}"