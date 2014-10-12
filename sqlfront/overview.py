


class Connection:
    """Run, execute, connection data"""

class Dialect:
    """Constructs Commands"""

class Command:
    """SQL string (maybe with templating functionality) """




class Query(Command + Connection):
    """Command + Connection """

class Cursor(Dialect + Connection):
    """Command + functionality to execute it. """
    

def example():
    with Cursor(config) as cursor:
        query = cursor.select(*arguments)
        results = query.run()