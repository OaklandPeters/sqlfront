from __future__ import absolute_import
import unittest

class ImportationTests(unittest.TestCase):
    def test_interfaces(self):
        if __name__ == "__main__":
            from sqlfront.interfaces import SQLDialect, SQLCommand, SQLConnection, SQLCursor, SQLInterface, SQLQuery
        else:
            from ..interfaces import SQLDialect, SQLCommand, SQLConnection, SQLCursor, SQLInterface, SQLQuery
    def test_mysql(self):
        if __name__ == "__main__":
            from sqlfront.mysql import MySQLDialect, MySQLCommand, MySQLConnection, MySQLCursor, MySQLInterface, MySQLQuery
        else:
            from ..mysql import MySQLDialect, MySQLCommand, MySQLConnection, MySQLCursor, MySQLInterface, MySQLQuery


if __name__ == "__main__":
    unittest.main()