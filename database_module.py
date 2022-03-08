import sqlite3

def open_connection():
	try:
		db_conn = sqlite3.connect("Library/bot_database.db")
	except:
		print("Error connecting to database!")
	return db_conn

def check_user_rights(user_id):
	db_conn = open_connection()
	cur = db_conn.cursor()
	cur.execute('SELECT * FROM `users` WHERE `id`="{}";'.format(user_id))
	row = cur.fetchone()
	db_conn.close()
	try:
		return row[1]
	except TypeError:
		return -1

def check_user_auth(user_id):
	db_conn = open_connection()
	cur = db_conn.cursor()
	cur.execute('SELECT * FROM `users` WHERE `id`="{}";'.format(user_id))
	row = cur.fetchone()
	db_conn.close()
	try:
		return row[2]
	except TypeError:
		return -1