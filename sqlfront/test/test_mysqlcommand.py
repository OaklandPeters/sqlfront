#
#python -m sqlfront/test/test_mysqlcommand

#from __future__ import absolute_import

import unittest
import collections
#
from sqlfront.mysql.mysqlcommand import MySQLCommand
from sqlfront.interfaces.sqlcommand import SQLCommand
from sqlfront.extern.stringtemplate import StringTemplate

class MySQLCommandTests(unittest.TestCase):
    def setUp(self):
        self.instring = "SELECT count(*) FROM users;"
        self.cmd = MySQLCommand(self.instring)
    def test_class_types(self):
        self.assert_(issubclass(MySQLCommand, str))
        self.assert_(issubclass(MySQLCommand, basestring))
        self.assert_(issubclass(MySQLCommand, StringTemplate))
        self.assert_(issubclass(MySQLCommand, SQLCommand))
        self.assert_(issubclass(MySQLCommand, collections.Sequence))
        self.assert_(not issubclass(MySQLCommand, collections.MutableSequence))
        
    def test_instance_types(self):
        self.assert_(isinstance(self.cmd, str))
        self.assert_(isinstance(self.cmd, StringTemplate))
        self.assert_(isinstance(self.cmd, basestring))
        self.assert_(isinstance(self.cmd, SQLCommand))
        self.assert_(isinstance(self.cmd, MySQLCommand))
        self.assert_(isinstance(self.cmd, collections.Sequence))
        self.assert_(not isinstance(self.cmd, collections.MutableSequence))
    def func_comparison(self, func):
        self.assertEqual(func(self.cmd), func(self.instring))
    def test_methods(self):        
        self.func_comparison(repr)
        self.assertEqual(self.cmd, self.instring)
        self.func_comparison(repr)
        self.func_comparison(str)        
        
        # Test some string methods
        repl = lambda S: S.replace(" ", "X")
        self.func_comparison(repl)
        adder = lambda S: S + " blah"
        self.func_comparison(adder)
        capit = lambda S: S.capitalize()
        self.func_comparison(capit)
    def test_format(self):
        template = "SELECT {column} FROM {table};"
        cmd = MySQLCommand(template)
        keywords = {'column': 'id', 'table':'users'}
        
        formt = lambda S: S.format(**keywords)
        self.func_comparison(formt)
    

if __name__ == "__main__":
    unittest.main()
