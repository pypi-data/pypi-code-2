# dbwrap - Simple convenience methods for Python DB-API 2.0 connections
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
#

from cStringIO import StringIO

__all__ = ['row', 'rowset', 'table', 'database']
__version__ = '0.3.2'

class row(dict):
	"""Default class for individual rows in a table"""
	id_key = "id"

	def __getattr__(self, key):
		try:
			return self[key]
		except KeyError:
			raise AttributeError(key)

	def __setattr__(self, key, value):
		self[key] = value
	
	def __delattr__(self, key):
		del self[key]

	def __reduce__(self):
		return (type(self), (dict(self),))

class rowset(object):
	"""A lazy reference to a set of rows.

	Again, this should not be instantiated by hand; use table.rows(...)
	"""
	def __init__(self, con, table, where_clause, args):
		self.con, self.table = con, table
		self.args = args # Any values for filled in parameters
		self.where_clause = ('WHERE ' + where_clause) if where_clause else ''
	
	def _set_clause(self, **kwargs):
		return ', '.join('%s = %s' % (column, self.con.placeholder) for column in kwargs.keys())

	def select(self, *args):
		"""Returns all rows in this rows_ref. If arguments are given, they are the columns selected."""
		return self.con._query_custom('SELECT %s FROM %s %s' % (
				', '.join(args) if args else '*',
				self.table.name,
				self.where_clause,
			),
			self.table.row,
			self.args
		)
	
	def select_one(self, *args):
		"""Returns the first row in this rows_ref. If arguments are given, they are the columns selected."""
		return self.con._query_one_custom('SELECT %s FROM %s %s' % (
				', '.join(args) if args else '*',
				self.table.name,
				self.where_clause,
			),
			self.table.row,
			self.args
		)

	def select_column(self, column):
		"""Returns the values in the specified column as a list."""
		results = self.con._query_custom('SELECT %s FROM %s %s' % (
				column,
				self.table.name,
				self.where_clause,
			),
			self.table.row,
			self.args
		)

		if not results:
			return []

		return [getattr(row, column) for row in results]

	def select_value(self, column):
		"""Returns the value in the specified column."""
		result = self.con._query_one_custom('SELECT %s FROM %s %s' % (
				column,
				self.table.name,
				self.where_clause,
			),
			self.table.row,
			self.args
		)

		if not result:
			return None

		return getattr(result, column)

	def update(self, _clause = '', *args, **values):
		"""Updates rows in this rows_ref.
		
		Note: this uses similar arguments to table.select()"""
		self.con.execute('UPDATE %s SET %s %s' % (
				self.table.name,
				_clause if _clause else self._set_clause(**values),
				self.where_clause),
			*((args if _clause else tuple(values.values())) + tuple(self.args))
		)

	def delete(self):
		"""Deletes all rows in this rows_ref"""
		self.con.execute('DELETE FROM %s %s' % (self.table.name, self.where_clause), *self.args)
	
	def __len__(self):
		return self.select_value('COUNT(*)')

	def exist(self):
		"""Returns whether this is not an empty set"""
		return len(self) != 0
	
class table(object):
	"""Default class for tables in a database.

	Note that you shouldn't instantiate this yourself; use wrapper['table-name'] or wrapper.table_name instead.
	"""

	def __init__(self, con, name):
		self.con, self.name = con, name
	
	def _where_clause(self, *args, **criteria):
		return ' AND '.join(('%s = ' + ('%' + self.con.placeholder if self.con.placeholder.startswith('%') else self.con.placeholder) if value is not None else '%s IS NULL') % column for column, value in zip(criteria.keys(), args or criteria.values()))

	def _create_clause(self, _query, args, criteria):
		return _query if _query else self._where_clause(*args, **criteria)

	def insert(self, _columns = [], _clause = '', *args, **values):
		"""INSERTs a row into the table.

		If columns and _clause are given, they will be placed into the SQL statement; otherwise, the columns and VALUES will be automatically generated.
		Note that columns _must_ be given if clause is.
		"""

		cur = self.con.execute('INSERT INTO %s(%s) %s' % (self.name, ', '.join(_columns if _columns else values.keys()), _clause if _clause else 'VALUES(%s)' % ', '.join([self.con.placeholder] * len(args if args else values))), *(values.values() if values else args))

		if hasattr(cur, 'lastrowid'):
			return cur.lastrowid

	def all(self):
		"""Returns the whole table"""

		return self.con._query_custom('SELECT * FROM %s' % self.name, self.row)

	def select(self, _query = '', *args, **criteria):
		"""SELECTs from the table.

		If _query is specified, it will be used as the where clause; otherwise, one will be generated from the keyword arguments.
		"""

		return self.rows(_query, *args, **criteria).select()

	def select_one(self, _query = '', *args, **criteria):
		"""SELECTs one row from the table.

		If _query is specified, it will be used as the where clause; otherwise, one will be generated from the keyword arguments.
		"""
		return self.rows(_query, *args, **criteria).select_one()

	def rows(self, _query = '', *args, **criteria):
		"""Returns a rows_ref object; uses same arguments as select()."""
		return rowset(self.con, self, self._create_clause(_query, args, criteria), (args if _query else tuple(x for x in criteria.values() if x is not None)))
	
	def __len__(self):
		return self.rows().select_value('COUNT(*)')

	row = row

class database(object):
	"""A wrapper for a DB-API connection. You MUST specify the placeholder for parameters in the call to __init__; this is ? for most libraries and %s for MySQLdb.

	If table_classes is specified, it must be a dict of classes that dbwrap will use instead of `table` for those tables. Notes:
		* The class must take a single argument, which is a reference to the parent wrapper.
		* The class is only instantiated once per database, and cached thereafter.

	NOTE: If your table names are not valid Python identifiers, you can access them with wrapper['table-name'].
	"""
	def __init__(self, con, placeholder, table_classes = None, debug = False):
		self.con, self.debug = con, debug
		self.placeholder = placeholder
		self.table_classes = table_classes or {}
		self._accessed_tables = {}
	
	def __getattr__(self, key):
		"""Returns a table object"""

		if key in self.__dict__:
			return self.__dict__[key]
		elif key in self.table_classes:
			return self._accessed_tables[key] if key in self._accessed_tables else self._accessed_tables.setdefault(key, self.table_classes[key](self))
		else:
			 return table(self, key)

	def commit(self):
		"""Commits the transaction"""
		self.con.commit()

	def execute(self, query, *args):
		"""Runs self.con.cursor().execute(query, *args), and returns the cursor"""

		if self.debug: print query, args

		cur = self.con.cursor()
		cur.execute(query, args)

		return cur

	def execute_script(self, script):
		"""Execute the SQL in `script` (can be a fileobj or string)"""
		if isinstance(script, basestring):
			script = StringIO(script)

		while True:
			command = ''
			while not command.rstrip().endswith(';'):
				data = script.readline()
				if data == '': break

				command += data

			command = command.strip()

			if command:
				self.execute(command)
			if data == '': return

	def execute_script_file(self, filename):
		"""Runs the SQL script in 'filename'"""

		self.execute_script(file(filename, 'r'))

	def query(self, query, *args):
		"""Wrapper similar to execute for SELECT statements, that returns a list of dicts."""

		self.query(query, row, args)
	
	def _query_custom(self, query, row_class = row, args = ()):
		cur = None
		sets = []

		if self.debug:
			print query, args
			self.debug = False
			cur = self.execute(query, *args)
			self.debug = True
		else:
			cur = self.execute(query, *args)

		def add_result():
			results = cur.fetchall()
			if cur.description and results:
				# all SELECTs should have a description, but we shouldn't choke as the result of idiots
				columns = [desc[0] for desc in cur.description]
				sets.append([row_class(zip(columns, result)) for result in results])
			else: sets.append([])

		add_result()
		while hasattr(cur, 'nextset') and cur.nextset():
			add_result()

		return sets[0] if len(sets) == 1 else sets

	def query_one(self, query, *args):
		"""Derivative of query for one-row SELECTs."""

		self._query_one_custom(self, query, row, args)
	
	def _query_one_custom(self, query, row_class = row, args = ()):
		cur = None

		if self.debug:
			print query, args
			self.debug = False
			cur = self.execute(query, *args)
			self.debug = True
		else:
			cur = self.execute(query, *args)

		result = cur.fetchone()
		while result is None:
			if not (hasattr(cur, 'nextset') and cur.nextset()): break
			result = cur.fetchone()
		if cur.description and result:
			columns = (desc[0] for desc in cur.description)
			return row_class(zip(columns, result))
		else:
			return None

	__getitem__ = __getattr__

	def __del__(self):
		del self.con

