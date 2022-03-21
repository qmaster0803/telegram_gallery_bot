import os
import config_module
import sqlite3 #for creating databases for new galleries
import requests
import string
import random
import hashlib

def create_new_gallery(gallery_id):
    if(str(gallery_id) not in os.listdir(config_module.library_path)):
        gallery_path = os.path.join(config_module.library_path, str(gallery_id))
        os.mkdir(gallery_path)
        db_conn = sqlite3.connect(os.path.join(gallery_path, "gallery.db"))
        cur = db_conn.cursor()
        cur.execute('CREATE TABLE "photos" ("id" INTEGER UNIQUE, "date" INTEGER, "checksum" TEXT, "size" INTEGER, PRIMARY KEY("id" AUTOINCREMENT));')
        db_conn.commit()
        db_conn.close()
        return 0
    else:
        print("Error creating directory for new gallery (id {}). Path already exists.".format(gallery_id))
        return 1

def check_photo_ext(filename):
    if(os.path.splitext(filename)[1].lower() in [".jpg", ".jpeg", ".png", ".heic"]): return True
    else: return False

def _generate_id(size=32, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def download(url, local_name): #DEPRICATED because of local server
    print("Downloading:", url)
    os.makedirs(config_module.downloads_path, exist_ok=True)
    r = requests.get(url, allow_redirects=True)
    local_filepath = os.path.join(config_module.downloads_path, local_name+os.path.splitext(url)[1])
    with open(local_filepath, 'wb') as file:
        file.write(r.content)
    return local_filepath

def copy_to_tmp(origin_path, local_name):
    print("Copying:", origin_path)
    os.makedirs(config_module.downloads_path, exist_ok=True)
    local_filepath = os.path.join(config_module.downloads_path, local_name+os.path.splitext(origin_path)[1])
    os.rename(origin_path, local_filepath)
    return local_filepath

def md5_of_file(path):
    hash_md5 = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()