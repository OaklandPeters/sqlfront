
#from __future__ import absolute_import

import unittest
import pdb
#
from sqlfront.mysql import MySQLConnection, MySQLDialect
from sqlfront.interfaces import SQLConnection, SQLDialect


class SDTest(SQLDialect):
    def __init__(self, things):
        self.things = things
class MSDTest(MySQLDialect):
    def __init__(self, things):
        self.things = things
class SCTest(SQLDialect):
    def __init__(self, things):
        self.things = things
class MCTest(SQLConnection, MySQLDialect):
    def __init__(self, things):
        self.things = things



print('Try SDTest("aa")')
print(MySQLConnection.__new__)
import pdb
pdb.set_trace()
print(MySQLConnection.__new__)

class MySQLConnectionTests(unittest.TestCase):
    def setUp(self):
        pass
    def test_init_config(self):
        cxn = MySQLConnection(config='connection.json')
        self.assert_(isinstance(cxn, MySQLConnection))
    def test_class_types(self):
        self.assert_(issubclass(MySQLConnection, SQLConnection))
        self.assert_(issubclass(MySQLConnection, MySQLDialect))
        self.assert_(issubclass(MySQLConnection, SQLDialect))

    def test_instance_types(self):
        cxn = MySQLConnection(config='connection.json')
        self.assert_(isinstance(cxn, SQLDialect))
        self.assert_(isinstance(cxn, MySQLDialect))
        self.assert_(isinstance(cxn, SQLConnection))
        self.assert_(isinstance(cxn, MySQLConnection))
        
    # def test_parameters(self):
    #
    # def test_context_manager(self):
    #
    

if __name__ == "__main__":
    unittest.main()