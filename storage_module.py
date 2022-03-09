import os
import config_module
import sqlite3 #for creating databases for new galleries

def create_new_gallery(gallery_id):
	if(str(gallery_id) not in os.listdir(config_module.library_path)):
		gallery_path = os.path.join(config_module.library_path, str(gallery_id))
		os.mkdir(gallery_path)
		db_conn = sqlite3.connect(os.path.join(gallery_path, "gallery.db"))
		cur = db_conn.cursor()
		cur.execute('CREATE TABLE "photos" ("id" INTEGER UNIQUE, "date" INTEGER, "checksum" TEXT, PRIMARY KEY("id"));')
		db_conn.commit()
		db_conn.close()
		return 0
	else:
		print("Error creating directory for new gallery (id {}). Path already exists.".format(gallery_id))
		return 1