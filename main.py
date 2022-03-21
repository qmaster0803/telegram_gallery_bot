import cv2
import os
import telebot
import photos_module
import config_module
import database_module
import large_messages
import storage_module
import threading
import time
import tempfile
from datetime import datetime

telebot.apihelper.API_URL = config_module.server_url
bot = telebot.TeleBot(config_module.bot_token, parse_mode=None)
database_module.init_database()

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
    elif(user_rights == 0):
        bot.send_message(message.chat.id, large_messages.user_help_message)
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
            new_gallery_id = database_module.create_new_gallery(new_gallery_name)
            if(new_gallery_id != -1):
                mkdir_result = storage_module.create_new_gallery(new_gallery_id) #creates dir and database with create_preview_table
                if(mkdir_result == 0): bot.send_message(message.chat.id, "New gallery with id {} successfully created!".format(new_gallery_id))
                else: bot.send_message(message.chat.id, "System error happened! Please contact system administrator.")
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
def generate_inline_keyboard_galleries_selection(input_array, marked=None):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row_width = 1
    for button in input_array:
        gallery_id = button.split()[1][:-1] #strange code here to get numeric id from button text
        if(marked != None and gallery_id.isnumeric() and int(marked) == int(gallery_id)): button = u'\u2705' + button
        markup.add(telebot.types.InlineKeyboardButton(button, callback_data="selectgallery "+gallery_id))
    return markup

def generate_inline_keyboard_months_selection(input_array, gallery_id):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row_width = 1
    for button in input_array:
        year, month, photos_count = button
        if(year != None and month != None): #photos without exif marked as None/None
            callback_data = "selectmonth "+str(year)+" "+str(month)+" "+str(gallery_id)
            button_text = datetime(year=year, month=month, day=1).strftime("%b %Y") + " - "+str(photos_count)+" photo(s)"
        else:
            callback_data = "selectmonth 0000 00 "+str(gallery_id)
            button_text = "Without date - "+str(photos_count)+" photo(s)"
        markup.add(telebot.types.InlineKeyboardButton(button_text, callback_data=callback_data))
    return markup

@bot.message_handler(commands=["selectgallery"])
def selectgallery_cmd(message):
    user_rights = database_module.check_user_rights(message.chat.id)
    if(user_rights == 1 or user_rights == 0):
        reply_markup = generate_inline_keyboard_galleries_selection(database_module.get_galleries_list(message.chat.id), marked=database_module.get_current_working_gallery(message.chat.id))
        bot.send_message(message.chat.id, "Select gallery:", reply_markup=reply_markup)
    else: bot.send_message(message.chat.id, "Permission denied")

@bot.message_handler(commands=["month"])
def month_cmd(message):
    user_rights = database_module.check_user_rights(message.chat.id)
    if(user_rights == 1 or user_rights == 0):
        working_gallery = database_module.get_current_working_gallery(message.chat.id)
        if(working_gallery != None):
            gallery_db_path = os.path.join(config_module.library_path, str(working_gallery), "gallery.db")
            months = database_module.find_months_in_gallery(gallery_db_path)
            if(months == None): bot.send_message(message.chat.id, "There are no photos in gallery!")
            else:
                reply_markup = generate_inline_keyboard_months_selection(months, working_gallery)
                gallery_name = database_module.get_gallery_info(working_gallery)[1]
                bot.send_message(message.chat.id, "Gallery: "+gallery_name+"\nSelect month:", reply_markup=reply_markup)
        else: bot.send_message(message.chat.id, "Please select gallery first!")
    else: bot.send_message(message.chat.id, "Permission denied")

@bot.message_handler(content_types=["photo"])
def photo_handler(message):
    user_rights = database_module.check_user_rights(message.chat.id)
    if(user_rights == 1 or user_rights == 0): bot.send_message(message.chat.id, "Error! Please send your photos as files to prevent compression.")
    else: bot.send_message(message.chat.id, "Permission denied")

@bot.message_handler(content_types=["document"])
def doc_handler(message):
    user_rights = database_module.check_user_rights(message.chat.id)
    if(user_rights == 1 or user_rights == 0):
        working_gallery = database_module.get_current_working_gallery(message.chat.id)
        if(working_gallery != None):
            if(storage_module.check_photo_ext(message.document.file_name)):
                if(message.document.file_size > 20971520): #20 MB
                    bot.send_message(message.chat.id, "Sorry, but only files under 20 MB supported now!")
                else:
                    file_info = bot.get_file(message.document.file_id)
                    file_url = 'https://api.telegram.org/file/bot{}/{}'.format(config_module.bot_token, file_info.file_path)
                    #file_unique_id and chat_id combination is used as local filename in downloads folder to prevent async conflicts
                    local_filepath = storage_module.download(file_url, str(file_info.file_unique_id)+str(message.chat.id))
                    database_module.add_to_queue(local_filepath, message.chat.id, database_module.get_current_working_gallery(message.chat.id), "add")
                    bot.delete_message(message.chat.id, message.id)
            else: bot.send_message(message.chat.id, "Unsupported file type! Currently I support *.jpg, *.jpeg, *.png and *.heic files.")
        else: bot.send_message(message.chat.id, "Please select gallery first!")
    else: bot.send_message(message.chat.id, "Permission denied")

#----------------------------------------------------------------------------------------------------
# CALLBACK HANDLER
#----------------------------------------------------------------------------------------------------
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
            reply_markup = generate_inline_keyboard_galleries_selection(database_module.get_galleries_list(call.message.chat.id), marked=gallery_id)
            bot.edit_message_text(call.message.text, call.message.chat.id, call.message.id, reply_markup=reply_markup) #do not change the text of message, change only inline keyboard
            bot.answer_callback_query(call.id, "Working gallery changed successfully!")
        else: bot.answer_callback_query(call.id, "Error!")

    #callback for inline keyboard of /month command
    if(call.data.startswith("selectmonth")):
        selected_year = int(call.data.split()[1])
        selected_month = int(call.data.split()[2])
        selected_gallery = int(call.data.split()[3])

        if(database_module.check_gallery_not_deleted(selected_gallery)):
            if(selected_gallery in database_module.get_user_galleries(call.message.chat.id) or database_module.check_user_rights(call.message.chat.id) == 1):
                bot.answer_callback_query(call.id, "Please wait...")
                gallery_db_path = os.path.join(config_module.library_path, str(selected_gallery), "gallery.db")
                batch = database_module.select_all_photos_of_month(gallery_db_path, selected_gallery, selected_year, selected_month, use_thumbs=True)
                preview_tables = photos_module.create_preview_table(batch)
                #using tempfile as buffer
                if(len(preview_tables) == 1):
                    temp = tempfile.TemporaryFile()
                    temp.write(preview_tables[0])
                    temp.seek(0)
                    visible_file_name = str(selected_gallery)+"-"+str(selected_month)+"."+str(selected_year)+"_preview.jpeg"
                    bot.send_document(call.message.chat.id, temp, visible_file_name=visible_file_name)
                else:
                    print("Got multiple tables:", len(preview_tables))
                    for i, table in enumerate(preview_tables):
                        temp = tempfile.TemporaryFile()
                        temp.write(table)
                        temp.seek(0)
                        visible_file_name = str(selected_gallery)+"-"+str(selected_month)+"."+str(selected_year)+"_preview-"+str(i)+".jpeg"
                        bot.send_document(call.message.chat.id, temp, visible_file_name=visible_file_name)
                        del temp

            else:
                bot.edit_message_text("Access denied!", call.message.chat.id, call.message.id, reply_markup=None)
                bot.answer_callback_query(call.id, "Access denied!")
        else:
            bot.edit_message_text("Gallery deleted!", call.message.chat.id, call.message.id, reply_markup=None)
            bot.answer_callback_query(call.id, "Gallery deleted!")
        

#----------------------------------------------------------------------------------------------------
# INTERNAL PROCESSING FUNCTIONS
#----------------------------------------------------------------------------------------------------
def process_queue(stop_event):
    while(True):
        if(database_module.check_processing_queue_available("add") > 0):
            file = database_module.get_file_from_queue("add") #return [id, path, user_id, gallery_id]

            if(os.path.splitext(file[1])[1].lower() == ".heic"):
                file = list(file)
                photos_module.heic_to_jpg(file[1])
                os.remove(file[1])
                file[1] = os.path.splitext(file[1])[0]+".jpg"

            gallery_db_path = os.path.join(config_module.library_path, str(file[3]), "gallery.db")
            try:
                photo_date = photos_module.get_photo_date(file[1])
            except:
                bot.send_document(file[2], open(file[1], 'rb'), caption="This photo cannot be processed!")
                os.remove(file[1])
            else:
                md5_hash = storage_module.md5_of_file(file[1])
                photo_size = os.path.getsize(file[1])

                if(not database_module.check_photo_exists(gallery_db_path, photo_size, md5_hash)):
                    #adding to system
                    #currently processing only photos (TODO)
                    photo_id = database_module.add_photo_to_gallery(gallery_db_path, photo_date, md5_hash, photo_size)
                    new_filepath = os.path.join(config_module.library_path, str(file[3]), str(photo_id)+os.path.splitext(file[1])[1])
                    os.rename(file[1], new_filepath) #move file from downloads dir to gallery dir
                    photos_module.create_preview(new_filepath, photo_id)
                else:
                    #file already exists
                    print(file[1])
                    bot.send_photo(file[2], open(file[1], 'rb'), caption="This photo already exists in this gallery!")
                    os.remove(file[1])

            database_module.delete_file_from_queue(file[0])
        else: time.sleep(1)
        if(stop_event.is_set()):
            print("Queue processing stoppped!")
            break


if(__name__ == "__main__"):
    quit_event = threading.Event()
    processing_queue_thread = threading.Thread(target=process_queue, args=(quit_event,))
    processing_queue_thread.start()

    #if ctrl+c pressed, execution will be continued after this line
    bot.polling(non_stop=True)
    print("Stopping sub processes...")
    quit_event.set()