import pymysql

database_config = {	'host': 'localhost',
					'port': 3306,
					'user': 'root',
					'passwd': 'root',
					'db': 'experiment_tracker'}

def get_database_connection():
	database_connection = pymysql.connect(
		host = database_config['host'],
		port = database_config['port'],
		user = database_config['user'],
		passwd = database_config['passwd'],
		db = database_config['db'],
		cursorclass = pymysql.cursors.DictCursor)

	return database_connection