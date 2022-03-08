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
def welcome(message):
	bot.send_message(message.chat.id, "Welcome!")
	bot.send_message(message.chat.id, "Your chat id: "+str(message.chat.id))

	user_rights = database_module.check_user_rights(message.chat.id)
	if(user_rights == 1): user_type = "admin"
	elif(user_rights == 0): user_type = "user"
	else: user_type = "non-authorised"

	bot.send_message(message.chat.id, "Your permission level is: "+user_type)
	send_help(message)

@bot.message_handler(commands=['help'])
def help(message):
	user_rights = database_module.check_user_rights(message.chat.id)
	#for admins
	if(user_rights == 1):
		bot.send_message(large_messages.admin_help_message)

def check_password():
	bot.send_message()

bot.infinity_polling()
#print("Opening...")
#photos = [photos_module.open_photo("Library/1.jpg"), photos_module.open_photo("Library/2.jpg"), photos_module.open_photo("Library/3.jpg"), photos_module.open_photo("Library/4.jpg"), photos_module.open_photo("Library/5.jpg"), photos_module.open_photo("Library/6.jpg"), photos_module.open_photo("Library/7.jpg"), photos_module.open_photo("Library/8.jpg")]

#print("Working...")
#for i in range(len(photos)):
#	photos[i] = photos_module.crop_and_resize(photos[i], use_blackpage=True)

#cv2.imshow("test", photos_module.create_preview_table(photos))
#cv2.waitKey(0)