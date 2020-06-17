import pymysql
import time

class Experiment():
	parameters = dict()
	results = dict()

	def __init__(self, database_config, project_name, add_timestamp=True):
		self.database_config = database_config
		self.project_name = project_name
		self.database_connection = self.get_database_connection()

		cursor = self.database_connection.cursor()
		cursor._defer_warnings = True
		cursor.execute('CREATE TABLE IF NOT EXISTS ' + self.project_name + ' (id INT NOT NULL AUTO_INCREMENT, PRIMARY KEY (id));')
		self.database_connection.commit()
		cursor.close()

		if add_timestamp:
			self.parameters['timestamp'] = str(int(time.time()))

	def get_database_connection(self):
		try:
			database_connection = pymysql.connect(host = self.database_config['host'],
												  port = self.database_config['port'],
												  user = self.database_config['user'],
												  passwd = self.database_config['passwd'],
												  db = self.database_config['db'],
												  cursorclass = pymysql.cursors.DictCursor)

			return database_connection

		except pymysql.Error:
			print('Error while connecting to database server. Check database configuration and connectivity.')
			print('Database configuration used: ', self.database_config)
			raise

	def save_results(self, clear_results=True):
		cursor = self.database_connection.cursor()

		parameter_columns, parameter_values = self.create_sql_string(self.parameters, cursor)
		results_columns, results_values = self.create_sql_string(self.results, cursor)

		columns = parameter_columns + ', ' + results_columns
		values = parameter_values + ', ' + results_values

		cursor.execute('INSERT INTO ' + self.project_name + ' (' + columns + ') VALUES (' + values + ')')

		self.database_connection.commit()
		cursor.close()

		if clear_results:
			self.results.clear()

	def create_sql_string(self, dictionary, cursor):
		columns = ''
		values = ''
		for column_name, value in dictionary.items():
			if not self.does_column_already_exist(cursor, column_name):
				self.create_column(cursor, column_name, value) # create column in case it does not already exist

			columns += column_name + ','
			if type(value) is bool:
				values += '\'' + str(int(value)) + '\','
			else:
				values += '\'' + str(value) + '\','
		columns = columns[:-1]
		values = values[:-1]
		return columns, values

	existing_columns = []
	def does_column_already_exist(self, cursor, column_name):
		if column_name in self.existing_columns:
			return True

		else:
			cursor.execute('SHOW COLUMNS FROM ' + self.project_name + ' LIKE %(column_name)s;', {'table_name': self.project_name, 'column_name': column_name})
			does_column_already_exist = len(cursor.fetchall()) == 1
			if does_column_already_exist:
				self.existing_columns.append(column_name)
			return does_column_already_exist

	def create_column(self, cursor, column_name, value):
		if type(value) is bool:
			field_definition = 'BOOLEAN NULL DEFAULT NULL'
		elif type(value) is int:
			field_definition = 'INT NULL DEFAULT NULL'
		elif type(value) is float:
			field_definition = 'DOUBLE NULL DEFAULT NULL'
		else:
			field_definition = 'TEXT NULL DEFAULT NULL'

		cursor.execute('ALTER TABLE ' + self.project_name + ' ADD COLUMN ' + column_name + ' ' + field_definition +';')