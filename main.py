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
	#TODO

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
			if(database_module.add_user(new_user_uid, new_user_rights) == 1): bot.send_message(message.chat.id, "User with this uid are already registered. Use /modifyuser or /deluser instead.")
			else: bot.send_message(message.chat.id, "User added successfully!")
		else: bot.send_message(message.chat.id, "Invalid syntax!")
	else: bot.send_message(message.chat.id, "Permission denied")

@bot.message_handler(commands=['modifyuser'])
def modifyuser_cmd(message):
	user_rights = database_module.check_user_rights(message.chat.id)
	if(user_rights == 1):
		if(len(message.text.split()) == 3):
			mod_user_uid = message.text.split()[1]
			mod_user_rights = message.text.split()[2]
			if(database_module.modify_user(mod_user_uid, mod_user_rights) == 1): bot.send_message(message.chat.id, "User with this uid are not registered. Use /adduser instead.")
			else: bot.send_message(message.chat.id, "User modified successfully!")
		else: bot.send_message(message.chat.id, "Invalid syntax!")
	else: bot.send_message(message.chat.id, "Permission denied")

@bot.message_handler(commands=["deluser"])
def deluser_cmd(message):
	user_rights = database_module.check_user_rights(message.chat.id)
	if(user_rights == 1):
		if(len(message.text.split()) == 2):
			del_user_uid = message.text.split()[1]
			if(database_module.delete_user(del_user_uid) == 1): bot.send_message(message.chat.id, "User with this uid are not registered.")
			else: bot.send_message(message.chat.id, "User deleted successfully!")
		else: bot.send_message(message.chat.id, "Invalid syntax!")
	else: bot.send_message(message.chat.id, "Permission denied")

@bot.message_handler(commands=["allowgallery"])
def allowgallery_cmd(message):
	user_rights = database_module.check_user_rights(message.chat.id)
	if(user_rights == 1):
		if(len(message.text.split()) == 3):
			mod_gallery_id = message.text.split()[1]
			mod_user_id = message.text.split()[2]
			if(database_module.allow_gallery(mod_user_id, mod_gallery_id) == 1): bot.send_message(message.chat.id, "Error. User or gallery doesn't exists or user has acess to this gallery already.")
			else: bot.send_message(message.chat.id, "User modified successfully!")
		else: bot.send_message(message.chat.id, "Invalid syntax!")
	else: bot.send_message(message.chat.id, "Permission denied")

@bot.message_handler(commands=["denygallery"])
def denygallery_cmd(message):
	user_rights = database_module.check_user_rights(message.chat.id)
	if(user_rights == 1):
		if(len(message.text.split()) == 3):
			mod_gallery_id = message.text.split()[1]
			mod_user_id = message.text.split()[2]
			if(database_module.deny_gallery(mod_user_id, mod_gallery_id) == 1): bot.send_message(message.chat.id, "Error. User doesn't exists or has no acess to this gallery already.")
			else: bot.send_message(message.chat.id, "User modified successfully!")
		else: bot.send_message(message.chat.id, "Invalid syntax!")
	else: bot.send_message(message.chat.id, "Permission denied")

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
		else: bot.send_message(message.chat.id, "Invalid syntax!")
	else: bot.send_message(message.chat.id, "Permission denied")

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
		else: bot.send_message(message.chat.id, "Invalid syntax!")
	else: bot.send_message(message.chat.id, "Permission denied")

@bot.message_handler(commands=['listgalleries'])
def listgalleries_cmd(message):
	user_rights = database_module.check_user_rights(message.chat.id)
	if(user_rights == 1 or user_rights == 0):
		galleries_list = ""
		batch = database_module.get_galleries_list(message.chat.id)
		for i, gallery in enumerate(batch):
			galleries_list += gallery
			if(i != len(batch)-1): galleries_list += "\n"
		bot.send_message(message.chat.id, galleries_list)

#----------------------------------------------------------------------------------------------------
# CASUAL COMMANDS HANDLERS
#----------------------------------------------------------------------------------------------------
def generate_inline_keyboard_by_list(input_array, marked=None):
	markup = telebot.types.InlineKeyboardMarkup()
	markup.row_width = 1
	for button in input_array:
		gallery_id = button.split()[1][:-1] #strange code here to get numeric id from button text
		if(marked != None and gallery_id.isnumeric() and int(marked) == int(gallery_id)): button = u'\u2705' + button
		markup.add(telebot.types.InlineKeyboardButton(button, callback_data="selectgallery "+gallery_id))
	return markup

@bot.message_handler(commands=["selectgallery"])
def selectgallery_cmd(message):
	user_rights = database_module.check_user_rights(message.chat.id)
	if(user_rights == 1 or user_rights == 0):
		reply_markup = generate_inline_keyboard_by_list(database_module.get_galleries_list(message.chat.id), marked=database_module.get_current_working_gallery(message.chat.id))
		bot.send_message(message.chat.id, "Select gallery:", reply_markup=reply_markup)
	else: bot.send_message(message.chat.id, "Permission denied")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
	#callback for inline keyboard of /selectgallery command
	if(call.data.startswith("selectgallery")):
		try: gallery_id = int(call.data.split()[1])
		except ValueError: #sometimes this happens if user presses on "There are nothing here!" button below gallery selection
			bot.answer_callback_query(call.id, "There are nothing here!")
			return 
		if(database_module.select_working_gallery(call.message.chat.id, gallery_id) == 0):
			#mark selected gallery with unicode char
			reply_markup = generate_inline_keyboard_by_list(database_module.get_galleries_list(call.message.chat.id), marked=gallery_id)
			bot.edit_message_text(call.message.text, call.message.chat.id, call.message.id, reply_markup=reply_markup) #do not change the text of message, change only inline keyboard
			bot.answer_callback_query(call.id, "Working gallery changed successfully!")
		else: bot.answer_callback_query(call.id, "Error!")


bot.infinity_polling()
#print("Opening...")
#photos = [photos_module.open_photo("Library/1.jpg"), photos_module.open_photo("Library/2.jpg"), photos_module.open_photo("Library/3.jpg"), photos_module.open_photo("Library/4.jpg"), photos_module.open_photo("Library/5.jpg"), photos_module.open_photo("Library/6.jpg"), photos_module.open_photo("Library/7.jpg"), photos_module.open_photo("Library/8.jpg")]

#print("Working...")
#for i in range(len(photos)):
#	photos[i] = photos_module.crop_and_resize(photos[i], use_blackpage=True)

#cv2.imshow("test", photos_module.create_preview_table(photos))
#cv2.waitKey(0)