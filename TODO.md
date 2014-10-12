SQLFRONT:
-------------------------------------------

@todo: Test command.format - does it support partial formatting? IE interaction between StringTempalat and the newer .format functions (SQLCommand, MySQLCommand) 
@todo: Registeration of subclasses of SQLInterface - requires new metaclass, descended from ABCMeta
@todo: SQLCommand.format() - should retreive dialect from cls (so MySQLCommand retreives MySQLDialect) 



[] Setup SQLSyntax to be used by composition by SQLDialect
[] Add magicmethods:
	[] __repr__
		[] Dialect
		[] Interface
		[] Connection
	[] Connection : parameters: refactor as properties
		[] Abstracts inside SQLConnection
		[] Set inside MySQLConnection.__init__
			[] Consider property()
[] Transcribe object notes:
	[] To image:
	[] Add to documentation:
	() Overview per object: relationships
	() Place all in overview file, plus one per interface object.
[] Draft Sequence: SQLX() --> MySQLX --> test_MySQLX
	[] Connection
	[] Dialect
	[] Syntax
	[] Cursor
	[] Query
[] Add function(s) for smart-offset:

