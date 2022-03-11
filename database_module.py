import config_module
import storage_module
import sqlite3
import json
import os
import glob
from datetime import datetime

def open_connection(db_path=config_module.main_db_path):
    try:
        db_conn = sqlite3.connect(db_path)
    except:
        print("Error connecting to database!")
    return db_conn

def create_new_database():
    pass
    #TODO

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
    #if user was accessing working gallery using admin rights, reset working gallery
    if(get_current_working_gallery(user_id) not in get_user_galleries(user_id)):
        del cur
        cur = db_conn.cursor()
        cur.execute('UPDATE `users` SET `current_working_gallery`=-1 WHERE `id`={};'.format(user_id))
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

def check_gallery_not_deleted(gallery_id):
    db_conn = open_connection()
    cur = db_conn.cursor()
    cur.execute('SELECT `deleted` FROM `galleries` WHERE `id`={};'.format(gallery_id))
    deleted = cur.fetchone()[0]
    db_conn.close()
    return deleted == 0

#----------------------------------------------------------------------------------------------------
# GALLERIES MODIFYING FUNCTIONS
#----------------------------------------------------------------------------------------------------
def get_gallery_info(gallery_id):
    db_conn = open_connection()
    cur = db_conn.cursor()
    cur.execute('SELECT * FROM `galleries` WHERE `id`="{}";'.format(gallery_id))
    result = cur.fetchone()
    db_conn.close()
    return result

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
    cur.execute('SELECT * FROM `galleries`;')
    result = []
    if(check_user_rights(user_id) != 1): galleries_of_user = get_user_galleries(user_id)
    for gallery in cur.fetchall():
        if((check_user_rights(user_id) == 1 or gallery[0] in galleries_of_user) and gallery[2] == 0):
            result.append("ID {}: {}".format(gallery[0], gallery[1]))
    db_conn.close()

    if(len(result) == 0): result.append("There are nothing here!")
    return result

def add_photo_to_gallery(db_path, date, checksum, size): #returns id of file because of using auto-increment column in db
    db_conn = open_connection(db_path=db_path)
    cur = db_conn.cursor()
    if(date != None): cur.execute('INSERT INTO `photos` (`date`,`checksum`,`size`) VALUES ({}, "{}", {});'.format(date, checksum, size))
    else:             cur.execute('INSERT INTO `photos` (`date`,`checksum`,`size`) VALUES (NULL, "{}", {});'.format(checksum, size))
    db_conn.commit();
    #get id of inserted line
    cur = db_conn.cursor()
    if(date != None): cur.execute('SELECT `id` FROM `photos` WHERE `date`={} AND `checksum`="{}" AND `size`={};'.format(date, checksum, size))
    else:             cur.execute('SELECT `id` FROM `photos` WHERE `date` IS NULL AND `checksum`="{}" AND `size`={};'.format(checksum, size))
    new_line_id = cur.fetchone()[0]
    return new_line_id

def check_photo_exists(db_path, size, checksum):
    db_conn = open_connection(db_path=db_path)
    cur = db_conn.cursor()
    cur.execute('SELECT * FROM `photos` WHERE `size`={} AND `checksum`="{}";'.format(size, checksum))
    count = len(cur.fetchall())
    db_conn.close()
    return count != 0

def count_photos_in_month(db_path, year, month):
    db_conn = open_connection(db_path=db_path)
    #calculate timestamps range
    min_timestamp = int(datetime.timestamp(datetime(year=year, month=month, day=1)))
    if(month != 12): max_timestamp = int(datetime.timestamp(datetime(year=year, month=month+1, day=1))-1)
    else:            max_timestamp = int(datetime.timestamp(datetime(year=year+1, month=1, day=1))-1)     #01 Jan of next year as max timestamp if checking Dec
    #find photos between this timestamps
    cur = db_conn.cursor()
    cur.execute('SELECT `id` FROM `photos` WHERE `date`>={} AND `date`<={};'.format(min_timestamp, max_timestamp))
    count = len(cur.fetchall())
    db_conn.close()
    return count

def find_months_in_gallery(db_path):
    result = []
    db_conn = open_connection(db_path=db_path)

    #count entries without date
    cur = db_conn.cursor()
    cur.execute('SELECT `id` FROM `photos` WHERE `date` IS NULL;')
    entries_without_date = len(cur.fetchall())
    del cur
    #count entries with date
    cur = db_conn.cursor()
    cur.execute('SELECT `id` FROM `photos` WHERE `date` IS NOT NULL;')
    entries_with_date = len(cur.fetchall())
    del cur

    if(entries_without_date > 0): result.append([None, None, entries_without_date])
    if(entries_with_date > 0):
        #find first photo date in db
        cur = db_conn.cursor()
        cur.execute('SELECT `date` FROM `photos` WHERE `date` IS NOT NULL ORDER BY `date` ASC LIMIT 1;')
        first_date = cur.fetchone()[0]
        first_year = datetime.fromtimestamp(first_date).year
        first_month = datetime.fromtimestamp(first_date).month
        del cur
        #find last photo date in db
        cur = db_conn.cursor()
        cur.execute('SELECT `date` FROM `photos` WHERE `date` IS NOT NULL ORDER BY `date` DESC LIMIT 1;')
        last_date = cur.fetchone()[0]
        last_year = datetime.fromtimestamp(last_date).year
        last_month = datetime.fromtimestamp(last_date).month
        del cur
        #iterate throught monthes from first date to last date and check their existance
        if(first_year != last_year): #if we need to scan more than part of year
            for year in range(first_year, last_year+1):
                if(year == first_year):   month_range = range(first_month, 12+1) #iterate from first_month to 12
                elif(year == last_year):  month_range = range(1, last_month+1)   #iterate from 1 to last_month
                else:                     month_range = range(1, 12+1)           #iterate from 1 to 12
                for month in month_range:
                    count = count_photos_in_month(db_path, year, month)
                    if(count > 0): result.append([year, month, count])
        else:
            for month in range(first_month, last_month+1):
                count = count_photos_in_month(db_path, first_year, month)
                if(count > 0): result.append([first_year, month, count])
        return result
    if(entries_without_date + entries_with_date == 0): return None

def select_all_photos_of_month(db_path, gallery_id, year, month, use_thumbs=False):
    db_conn = open_connection(db_path=db_path)
    cur = db_conn.cursor()

    if(year != 0 and month != 0): #photos without exif marked as 0/0
        #calculate timestamps range
        min_timestamp = int(datetime.timestamp(datetime(year=year, month=month, day=1)))
        if(month != 12): max_timestamp = int(datetime.timestamp(datetime(year=year, month=month+1, day=1))-1)
        else:            max_timestamp = int(datetime.timestamp(datetime(year=year+1, month=1, day=1))-1)     #01 Jan of next year as max timestamp if checking Dec
        #find all photos between this timestamps
        cur.execute('SELECT `id` FROM `photos` WHERE `date`>={} AND `date`<={};'.format(min_timestamp, max_timestamp))
    else:
        cur.execute('SELECT `id` FROM `photos` WHERE `date` IS NULL;')
    photos = cur.fetchall()
    result_paths = []
    for photo_id in photos:
        #there are no file extensions, stored in database, so we can guess extension because of unique filenames
        if(use_thumbs): mask = os.path.join(config_module.library_path, str(gallery_id), str(photo_id[0])+"_thumb.*")
        else: mask = os.path.join(config_module.library_path, str(gallery_id), str(photo_id[0])+".*")
        result_paths.append(glob.glob(mask)[0])
    return result_paths

#----------------------------------------------------------------------------------------------------
# PHOTOS PROCESSING QUEUE FUNCTIONS
#----------------------------------------------------------------------------------------------------
def add_to_queue(path, user_id, gallery_id):
    db_conn = open_connection()
    cur = db_conn.cursor()
    cur.execute('INSERT INTO `processing_queue` (`path`, `user_id`, `gallery_id`) VALUES ("{}", {}, {});'.format(path, user_id, gallery_id))
    db_conn.commit()
    db_conn.close()

def check_processing_queue_available():
    db_conn = open_connection()
    cur = db_conn.cursor()
    cur.execute('SELECT * FROM `processing_queue`;')
    rowcount = len(cur.fetchall())
    db_conn.close()
    return rowcount

def get_file_from_queue():
    db_conn = open_connection()
    cur = db_conn.cursor()
    cur.execute('SELECT * FROM `processing_queue` ORDER BY `id` DESC LIMIT 1;')
    res = cur.fetchone()
    db_conn.close()
    return res

def delete_file_from_queue(file_id):
    db_conn = open_connection()
    cur = db_conn.cursor()
    cur.execute('DELETE FROM `processing_queue` WHERE `id`={};'.format(file_id))
    db_conn.commit()
    db_conn.close()

def check_queue_for_user(user_id):
    db_conn = open_connection()
    cur = db_conn.cursor()
    cur.execute('SELECT `id` FROM `processing_queue` WHERE `user_id`={};'.format(user_id))
    result = len(cur.fetchall())
    db_conn.close()
    return result