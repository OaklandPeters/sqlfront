from __future__ import absolute_import
import unittest

if __name__ == "__main__":
    from sqlfront.mysql import MySQLDialect, MySQLCommand, MySQLConnection, MySQLCursor, MySQLInterface, MySQLQuery, MySQLSyntax
    from sqlfront.interfaces import SQLDialect, SQLCommand, SQLConnection, SQLCursor, SQLInterface, SQLQuery, SQLSyntax
else:
    from ..mysql import MySQLDialect, MySQLCommand, MySQLConnection, MySQLCursor, MySQLInterface, MySQLQuery, MySQLSyntax
    from ..interfaces import SQLDialect, SQLCommand, SQLConnection, SQLCursor, SQLInterface, SQLQuery, SQLSyntax


class HeirarchyTests(unittest.TestCase):
    def check_ancestry(self, obj, *parents):
        self.assert_(issubclass(obj, SQLDialect))
        self.assert_(issubclass(obj, MySQLDialect))
        
        for parent in parents:
            self.assert_(issubclass(obj, parent))
        
    def test_roots(self):
        self.assert_(issubclass(MySQLDialect, SQLDialect))

    def test_mysqlcommand(self):
        self.check_ancestry(MySQLCommand, SQLCommand)

    def test_mysqlconnection(self):
        self.check_ancestry(MySQLConnection, SQLConnection)

    def test_mysqldialect(self):
        self.check_ancestry(MySQLInterface, SQLInterface)

    def test_mysqlcursor(self):
        self.check_ancestry(MySQLCursor, SQLCursor, MySQLInterface, MySQLConnection)

    def test_mysqlquery(self):
        self.check_ancestry(MySQLQuery, SQLQuery, MySQLCommand, MySQLConnection)
    
    def test_mysqlsyntax(self):
        self.check_ancestry(MySQLSyntax, SQLSyntax)



    def check_sql_registry(self, obj):
        self.assertEqual(
            {
                'dialect': SQLDialect,
                'interface': SQLInterface,
                'syntax': SQLSyntax,
                'connection': SQLConnection,
                'command': SQLCommand,
                'cursor': SQLCursor,
                'query': SQLQuery
            },
            obj.registry
        )
    def check_mysql_registry(self, obj):
        self.assertEqual({
                'dialect': MySQLDialect,
                'interface': MySQLInterface,
                'syntax': MySQLSyntax,
                'connection': MySQLConnection,
                'command': MySQLCommand,
                'cursor': MySQLCursor,
                'query': MySQLQuery
            },
            obj.registry
        )

    def test_sql_registry(self):
        self.check_sql_registry(SQLDialect)
        self.check_sql_registry(SQLInterface)
        self.check_sql_registry(SQLSyntax)
        self.check_sql_registry(SQLConnection)
        self.check_sql_registry(SQLCommand)
        self.check_sql_registry(SQLCursor)
        self.check_sql_registry(SQLQuery)
             
    def test_mysql_registry(self):
        self.check_mysql_registry(MySQLDialect)
        self.check_mysql_registry(MySQLInterface)
        self.check_mysql_registry(MySQLSyntax)
        self.check_mysql_registry(MySQLConnection)
        self.check_mysql_registry(MySQLCommand)
        self.check_mysql_registry(MySQLCursor)
        self.check_mysql_registry(MySQLQuery)
        

if __name__ == "__main__":
    unittest.main()