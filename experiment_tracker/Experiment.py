from experiment_tracker.database_connection import get_database_connection
import time

class Experiment():
	parameters = dict()
	results = dict()

	def __init__(self, project_name, add_timestamp=True):
		self.project_name = project_name
		cursor = get_database_connection().cursor()
		cursor._defer_warnings = True
		cursor.execute('CREATE TABLE IF NOT EXISTS ' + project_name + ' (id INT NOT NULL AUTO_INCREMENT, PRIMARY KEY (id));')

		if add_timestamp:
			self.parameters['timestamp'] = str(int(time.time()))

	def save_results(self, clear_results=True):
		def add_column_if_not_exists(cursor, column, value):
			cursor._defer_warnings = True
			if type(value) is bool:
				cursor.execute('ALTER TABLE ' + self.project_name + ' ADD COLUMN IF NOT EXISTS ' + column + ' BOOLEAN NULL DEFAULT NULL;');	
			if type(value) is int:
				cursor.execute('ALTER TABLE ' + self.project_name + ' ADD COLUMN IF NOT EXISTS ' + column + ' INT NULL DEFAULT NULL;', );
			elif type(value) is float:
				cursor.execute('ALTER TABLE ' + self.project_name + ' ADD COLUMN IF NOT EXISTS ' + column + ' DOUBLE NULL DEFAULT NULL;');
			else:
				cursor.execute('ALTER TABLE ' + self.project_name + ' ADD COLUMN IF NOT EXISTS ' + column + ' TEXT NULL DEFAULT NULL;');

		def create_sql_string(dictionary):
			columns = ''
			values = ''
			for column, value in dictionary.items():
				add_column_if_not_exists(cursor, column, value)
				columns += column + ','
				if type(value) is bool:
					values += '\'' + str(int(value)) + '\','
				else:
					values += '\'' + str(value) + '\','
			columns = columns[:-1]
			values = values[:-1]
			return columns, values

		database_connection = get_database_connection()
		cursor = database_connection.cursor()

		parameter_columns, parameter_values = create_sql_string(self.parameters)
		results_columns, results_values = create_sql_string(self.results)

		columns = parameter_columns + ', ' + results_columns
		values = parameter_values + ', ' + results_values

		database_connection = get_database_connection()
		cursor = database_connection.cursor()

		cursor.execute('INSERT INTO ' + self.project_name + ' (' + columns + ') VALUES (' + values + ')')

		database_connection.commit()
		cursor.close()

		if clear_results:
			self.results.clear()