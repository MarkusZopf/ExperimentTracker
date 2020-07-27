import pymysql
import time

class Experiment():

	def __init__(self, database_config, project_name, add_timestamp=True):
		self.parameters = dict()
		self.results = dict()

		self.database_config = database_config
		self.project_name = project_name
		
		database_connection = self.get_database_connection()
		cursor = database_connection.cursor()
		cursor._defer_warnings = True
		cursor.execute('CREATE TABLE IF NOT EXISTS ' + self.project_name + ' (id INT NOT NULL AUTO_INCREMENT, finished BOOLEAN DEFAULT NULL, PRIMARY KEY (id));')
		database_connection.commit()
		cursor.close()
		database_connection.close()

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

	def save_results(self, clear_results=True, set_finished=False):
		parameter_columns, parameter_values = self.create_sql_string(self.parameters)
		results_columns, results_values = self.create_sql_string(self.results)

		columns = parameter_columns + ', ' + results_columns
		values = parameter_values + ', ' + results_values

		if set_finished:
			columns = 'finished, ' + columns
			values = '1, ' + values

		database_connection = self.get_database_connection()
		cursor = database_connection.cursor()
		cursor.execute('INSERT INTO ' + self.project_name + ' (' + columns + ') VALUES (' + values + ')')
		database_connection.commit()
		cursor.close()
		database_connection.close()

		if clear_results:
			self.results.clear()

	def create_sql_string(self, dictionary):
		columns = ''
		values = ''
		for column_name, value in dictionary.items():
			if not self.does_column_already_exist(column_name):
				self.create_column(column_name, value) # create column in case it does not already exist

			columns += column_name + ','
			if type(value) is bool:
				values += '\'' + str(int(value)) + '\','
			else:
				values += '\'' + str(value) + '\','
		columns = columns[:-1]
		values = values[:-1]
		return columns, values

	existing_columns = []
	def does_column_already_exist(self, column_name):
		if column_name in self.existing_columns:
			return True

		else:
			database_connection = self.get_database_connection()
			cursor = database_connection.cursor()
			cursor.execute('SHOW COLUMNS FROM ' + self.project_name + ' LIKE %(column_name)s;', {'table_name': self.project_name, 'column_name': column_name})
			does_column_already_exist = len(cursor.fetchall()) == 1
			cursor.close()
			database_connection.close()

			if does_column_already_exist:
				self.existing_columns.append(column_name)
			return does_column_already_exist

	def create_column(self, column_name, value):
		if type(value) is bool:
			field_definition = 'BOOLEAN NULL DEFAULT NULL'
		elif type(value) is int:
			field_definition = 'INT NULL DEFAULT NULL'
		elif type(value) is float:
			field_definition = 'DOUBLE NULL DEFAULT NULL'
		else:
			field_definition = 'TEXT NULL DEFAULT NULL'

		database_connection = self.get_database_connection()
		cursor = database_connection.cursor()
		cursor.execute('ALTER TABLE ' + self.project_name + ' ADD COLUMN ' + column_name + ' ' + field_definition +';')
		cursor.close()
		database_connection.close()

	def does_row_already_exist(self, parameter_names):
		condition = ''
		for parameter_name in parameter_names:
			if not self.does_column_already_exist(parameter_name): 
				return False # a row with the specified values cannot exist if the corresponding column does not exist

			condition += parameter_name + '='
			value = self.parameters[parameter_name]
			if type(value) is bool:
				condition += str(int(value))
			elif type(value) is int or type(value) is float:
				condition += str(value)
			else:
				condition += '\'' + str(value) + '\''

			condition += ' AND '

		condition = condition[:-5]

		database_connection = self.get_database_connection()
		cursor = database_connection.cursor()
		cursor.execute('SELECT COUNT(*) FROM ' + self.project_name + ' WHERE ' + condition + ';')
		result = int(cursor.fetchone()['COUNT(*)']) > 0
		cursor.close()
		database_connection.close()
		
		return result

	def is_experiment_finished(self):
		"""Tests if an experiments with the same parameters (except of the timestamp) is already set as finished in the database."""

		condition = ''
		for parameter_name, parameter_value in self.parameters.items():
			if not self.does_column_already_exist(parameter_name):
				return False # an experiment with the specified parameter cannot exist if the corresponding column does not exist

			if parameter_name != 'timestamp':
				condition += parameter_name + '='
				parameter_value = self.parameters[parameter_name]
				if type(parameter_value) is bool:
					condition += str(int(parameter_value))
				elif type(parameter_value) is int or type(parameter_value) is float:
					condition += str(parameter_value)
				else:
					condition += '\'' + str(parameter_value) + '\''

				condition += ' AND '

		condition = condition[:-5]
		
		database_connection = self.get_database_connection()
		cursor = database_connection.cursor()
		cursor.execute('SELECT COUNT(*) FROM ' + self.project_name + ' WHERE finished = 1 AND ' + condition + ';')
		result = int(cursor.fetchone()['COUNT(*)']) > 0
		cursor.close()
		database_connection.close()

		return result