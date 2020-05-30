from experiment_tracker.database_connection import get_database_connection, database_config
import time

class Experiment():
	parameters = dict()
	results = dict()

	def __init__(self, project_name, add_timestamp=True):
		self.project_name = project_name
		self.database_connection = get_database_connection()

		cursor = self.database_connection.cursor()
		cursor._defer_warnings = True
		cursor.execute('CREATE TABLE IF NOT EXISTS ' + self.project_name + ' (id INT NOT NULL AUTO_INCREMENT, PRIMARY KEY (id));')
		self.database_connection.commit()
		cursor.close()

		if add_timestamp:
			self.parameters['timestamp'] = str(int(time.time()))

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

	def does_column_already_exist(self, cursor, column_name):
		cursor.execute('SHOW COLUMNS FROM ' + self.project_name + ' LIKE %(column_name)s;', {'table_name': self.project_name, 'column_name': column_name})
		does_column_already_exist = len(cursor.fetchall()) == 1
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