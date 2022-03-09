import storage_module
import sqlite3
import json

def open_connection():
	try:
		db_conn = sqlite3.connect(config_module.main_db_path)
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
	cur.execute('SELECT * FROM `users` WHERE `id`={};'.format(user_id))
	row = cur.fetchone()
	db_conn.close()
	try:
		return row[1]
	except TypeError:
		return -1

def get_user_galleries(user_id):
	db_conn = open_connection()
	cur = db_conn.cursor()
	cur.execute('SELECT `galleries` FROM `users` WHERE `id`={};'.format(user_id))
	galleries = cur.fetchone()[0]
	db_conn.close()
	return json.loads(galleries)

def allow_gallery(user_id, gallery_id):
	db_conn = open_connection()
	#check user exists
	cur = db_conn.cursor()
	cur.execute('SELECT * FROM `users` WHERE `id`={};'.format(user_id))
	if(cur.fetchone() == None): return 1
	#check gallery exists
	cur = db_conn.cursor()
	cur.execute('SELECT * FROM `galleries` WHERE `id`={} AND `deleted`=0;'.format(gallery_id))
	if(cur.fetchone() == None): return 1
	#reload json string here
	cur = db_conn.cursor()
	cur.execute('SELECT `galleries` FROM `users` WHERE `id`={};'.format(user_id))
	galleries_list = json.loads(cur.fetchone()[0])
	if(int(gallery_id) in galleries_list): return 1
	galleries_list.append(int(gallery_id))
	del cur
	cur = db_conn.cursor()
	cur.execute('UPDATE `users` SET `galleries`="{}" WHERE `id`={};'.format(json.dumps(galleries_list), user_id))
	db_conn.commit()
	db_conn.close()

def deny_gallery(user_id, gallery_id):
	db_conn = open_connection()
	#check user exists
	cur = db_conn.cursor()
	cur.execute('SELECT * FROM `users` WHERE `id`={};'.format(user_id))
	if(cur.fetchone() == None): return 1
	#reload json string here
	cur = db_conn.cursor()
	cur.execute('SELECT `galleries` FROM `users` WHERE `id`={};'.format(user_id))
	galleries_list = json.loads(cur.fetchone()[0])
	if(int(gallery_id) not in galleries_list): return 1
	galleries_list.remove(int(gallery_id))
	del cur
	cur = db_conn.cursor()
	cur.execute('UPDATE `users` SET `galleries`="{}" WHERE `id`={};'.format(json.dumps(galleries_list), user_id))
	db_conn.commit()
	#set user's working gallery to none (-1) if denied gallery was choosen
	cur = db_conn.cursor()
	cur.execute('UPDATE `users` SET `current_working_gallery`=-1 WHERE `id`={} AND `current_working_gallery`={};'.format(user_id, int(gallery_id)))
	db_conn.commit()
	db_conn.close()

def select_working_gallery(user_id, gallery_id):
	if(gallery_id in get_user_galleries(user_id) or check_user_rights(user_id) == 1):
		db_conn = open_connection()
		cur = db_conn.cursor()
		cur.execute('UPDATE `users` SET `current_working_gallery`={} WHERE `id`={};'.format(gallery_id, user_id))
		db_conn.commit()
		db_conn.close()
		return 0
	else: return 1

def get_current_working_gallery(user_id):
	db_conn = open_connection()
	cur = db_conn.cursor()
	cur.execute('SELECT `current_working_gallery` FROM `users` WHERE `id`={};'.format(user_id))
	cwg = cur.fetchone()[0]
	db_conn.close()
	if(int(cwg) == -1): return None
	else: return int(cwg)

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
	#reset all users that have this gallery as working to empty working gallery (-1)
	del cur
	cur = db_conn.cursor()
	cur.execute('UPDATE `users` SET `current_working_gallery`=-1 WHERE `current_working_gallery`={};'.format(gallery_id))
	db_conn.commit()
	db_conn.close()

def get_galleries_list(user_id):
	db_conn = open_connection()
	cur = db_conn.cursor()
	cur.execute("SELECT * FROM `galleries`;")
	result = []
	if(check_user_rights(user_id) != 1): galleries_of_user = get_user_galleries(user_id)
	for gallery in cur.fetchall():
		if((check_user_rights(user_id) == 1 or gallery[0] in galleries_of_user) and gallery[2] == 0):
			result.append("ID {}: {}".format(gallery[0], gallery[1]))
	db_conn.close()

	if(len(result) == 0): result.append("There are nothing here!")
	return result