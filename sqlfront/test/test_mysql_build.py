from __future__ import absolute_import
import unittest
import MySQLdb

class BuildTests(unittest.TestCase):
    def test_connect(self):
        
        db = MySQLdb.connect(host="127.0.0.1", user="sqlfront", db="test_sqlfront", port=3306, passwd='default')
        cxn = db.cursor()
        cxn.execute("SHOW tables;")
        results = cxn.fetchall()
        
        self.assertEqual(results, (('Orders', ), ('Persons', )))
        
        cxn.execute("SELECT count(*) FROM Orders")
        count = cxn.fetchall()
        self.assertEqual(count[0][0], 7)
        
        cxn.execute("SELECT count(*) FROM Orders")
        count = cxn.fetchall()
        self.assertEqual(count[0][0], 7)

        cxn.execute("SELECT count(*) FROM Persons")
        count = cxn.fetchall()
        self.assertEqual(count[0][0], 4)
        

if __name__ == "__main__":
    unittest.main()