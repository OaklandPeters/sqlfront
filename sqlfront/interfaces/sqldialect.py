from __future__ import absolute_import
from abc import ABCMeta, abstractmethod

class SQLDialect(object):
    __metaclass__ = ABCMeta
    registry = {}
    @abstractmethod
    def escape(self, obj):
        """Return a string version of an object, with characters
        escaped appropriately for this language."""
        return NotImplemented
    @abstractmethod
    def format(self, *args, **kwargs):
        """Apply formatting to command, after escaping all arguments."""
        return NotImplemented
