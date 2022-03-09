import cv2
import os
import telebot
import photos_module
import config_module
import database_module
import large_messages


bot = telebot.TeleBot(config_module.bot_token, parse_mode=None)
a = None

@bot.message_handler(commands=['start'])
def start_cmd(message):
	bot.send_message(message.chat.id, "Welcome!")
	bot.send_message(message.chat.id, "Your chat id: "+str(message.chat.id))

	user_rights = database_module.check_user_rights(message.chat.id)
	if(user_rights == 1): user_type = "admin"
	elif(user_rights == 0): user_type = "user"
	else: user_type = "non-authorised"

	bot.send_message(message.chat.id, "Your permission level is: "+user_type)
	help_cmd(message)

@bot.message_handler(commands=['help'])
def help_cmd(message):
	user_rights = database_module.check_user_rights(message.chat.id)
	#for admins
	if(user_rights == 1):
		bot.send_message(message.chat.id, large_messages.admin_help_message)

#----------------------------------------------------------------------------------------------------
# USER MODIFYING COMMANDS HANDLERS
#----------------------------------------------------------------------------------------------------
@bot.message_handler(commands=['adduser'])
def adduser_cmd(message):
	user_rights = database_module.check_user_rights(message.chat.id)
	if(user_rights == 1):
		if(len(message.text.split()) == 3):
			new_user_uid = message.text.split()[1]
			new_user_rights = message.text.split()[2]
			if(database_module.add_user(new_user_uid, new_user_rights) == 1):
				bot.send_message(message.chat.id, "User with this uid are already registered. Use /modifyuser or /deluser instead.")
			else:
				bot.send_message(message.chat.id, "User added successfully!")
		else:
			bot.send_message(message.chat.id, "Invalid syntax!")
	else:
		bot.send_message(message.chat.id, "Permission denied")

@bot.message_handler(commands=['modifyuser'])
def modifyuser_cmd(message):
	user_rights = database_module.check_user_rights(message.chat.id)
	if(user_rights == 1):
		if(len(message.text.split()) == 3):
			mod_user_uid = message.text.split()[1]
			mod_user_rights = message.text.split()[2]
			if(database_module.modify_user(mod_user_uid, mod_user_rights) == 1):
				bot.send_message(message.chat.id, "User with this uid are not registered. Use /adduser instead.")
			else:
				bot.send_message(message.chat.id, "User modified successfully!")
		else:
			bot.send_message(message.chat.id, "Invalid syntax!")
	else:
		bot.send_message(message.chat.id, "Permission denied")

@bot.message_handler(commands=["deluser"])
def deluser_cmd(message):
	user_rights = database_module.check_user_rights(message.chat.id)
	if(user_rights == 1):
		if(len(message.text.split()) == 2):
			del_user_uid = message.text.split()[1]
			if(database_module.delete_user(del_user_uid) == 1):
				bot.send_message(message.chat.id, "User with this uid are not registered.")
			else:
				bot.send_message(message.chat.id, "User deleted successfully!")
		else:
			bot.send_message(message.chat.id, "Invalid syntax!")
	else:
		bot.send_message(message.chat.id, "Permission denied")

#----------------------------------------------------------------------------------------------------
# GALLERIES MODIFYING COMMANDS HANDLERS
#----------------------------------------------------------------------------------------------------
@bot.message_handler(commands=["newgallery"])
def newgallery_cmd(message):
	user_rights = database_module.check_user_rights(message.chat.id)
	if(user_rights == 1):
		if(len(message.text.split()) == 2):
			new_gallery_name = message.text.split()[1]
			result = database_module.create_new_gallery(new_gallery_name)
			if(result != -1):
				bot.send_message(message.chat.id, "New gallery with id {} successfully created!".format(result))
			else:
				bot.send_message(message.chat.id, "Gallery with this name already exists!")

@bot.message_handler(commands=['delgallery'])
def delgallery_cmd(message):
	user_rights = database_module.check_user_rights(message.chat.id)
	if(user_rights == 1):
		if(len(message.text.split()) == 2):
			del_gallery_id = message.text.split()[1]
			if(database_module.delete_gallery(del_gallery_id) == 1):
				bot.send_message(message.chat.id, "Gallery with this id doesn't exist!")
			else:
				bot.send_message(message.chat.id, "Gallery succesfully deleted. You can restore it manually later.")

bot.infinity_polling()
#print("Opening...")
#photos = [photos_module.open_photo("Library/1.jpg"), photos_module.open_photo("Library/2.jpg"), photos_module.open_photo("Library/3.jpg"), photos_module.open_photo("Library/4.jpg"), photos_module.open_photo("Library/5.jpg"), photos_module.open_photo("Library/6.jpg"), photos_module.open_photo("Library/7.jpg"), photos_module.open_photo("Library/8.jpg")]

#print("Working...")
#for i in range(len(photos)):
#	photos[i] = photos_module.crop_and_resize(photos[i], use_blackpage=True)

#cv2.imshow("test", photos_module.create_preview_table(photos))
#cv2.waitKey(0)