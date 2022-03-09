import sqlite3

def open_connection():
	try:
		db_conn = sqlite3.connect("Library/bot_database.db")
	except:
		print("Error connecting to database!")
	return db_conn

#----------------------------------------------------------------------------------------------------
# USERS MODIFYING FUNCTIONS
#----------------------------------------------------------------------------------------------------
def add_user(user_id, rights):
	db_conn = open_connection()
	cur = db_conn.cursor()
	if(rights == '1' or rights == 'admin'): rights_id = 1
	else: rights_id = 0
	try:
		cur.execute('INSERT INTO `users` (`id`,`rights`) VALUES ({}, {});'.format(user_id, rights_id))
	except sqlite3.IntegrityError as e:
		if(str(e).startswith("UNIQUE constraint failed")):
			return 1
	db_conn.commit()
	db_conn.close()
	return 0

def modify_user(user_id, rights):
	db_conn = open_connection()
	cur = db_conn.cursor()
	if(rights == '1' or rights == 'admin'): rights_id = 1
	else: rights_id = 0
	cur.execute('UPDATE `users` SET `rights` = {} WHERE `id`={};'.format(rights_id, user_id))
	if(cur.rowcount == 0):
		return 1
	db_conn.commit()
	db_conn.close()
	return 0

def delete_user(user_id):
	db_conn = open_connection()
	cur = db_conn.cursor()
	cur.execute('DELETE FROM `users` WHERE `id`={};'.format(user_id))
	if(cur.rowcount == 0):
		return 1
	db_conn.commit()
	db_conn.close()
	return 0

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

#----------------------------------------------------------------------------------------------------
# GALLERIES MODIFYING FUNCTIONS
#----------------------------------------------------------------------------------------------------
def create_new_gallery(name):
	db_conn = open_connection()
	cur = db_conn.cursor()
	cur.execute('SELECT * FROM `galleries` WHERE `name`="{}";'.format(name))
	if(cur.fetchone() != None): return -1
	del cur
	cur = db_conn.cursor()
	cur.execute('INSERT INTO `galleries` (`name`) VALUES ("{}");'.format(name))
	db_conn.commit()
	cur = db_conn.cursor()
	cur.execute('SELECT `id` FROM `galleries` WHERE `name`="{}";'.format(name))
	new_gallery_id = cur.fetchone()[0]
	db_conn.close()
	return new_gallery_id

def delete_gallery(gallery_id):
	db_conn = open_connection()
	cur = db_conn.cursor()
	cur.execute('UPDATE `galleries` SET `deleted`=1 WHERE `id`={};'.format(gallery_id))
	db_conn.commit()
	db_conn.close()