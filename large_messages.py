admin_help_message = '''User modifying commands:
/adduser <user_id> <admin/user> - add user to bot system
/modifyuser <user_id> <admin/user> - modify user permissions
/deluser <user_id> - delete user without deleting content (manual action on server required)
/allowgallery <gallery_id> <user_id> - allow access to gallery for user
/denygallery <gallery_id> <user_id> - deny access to gallery for user

Galleries modifying commands:
/newgallery <name> - create new gallery
/delgallery <id> - delete gallery (without deleting content)
/listgalleries - list all galleries
(TODO)/renamegallery <id> <new_name>- rename existing gallery
(TODO)/galleryinfo <id> - show all info about selected gallery
(TODO)/autorotate <id> <enable/disable> - enable or disable autorotate prompt for gallery

Casual commands:
/selectgallery - select working gallery
/preview_month - show the selected month as preview of images
/download_month - download all photos of the selected month

Send a photo to save it.'''

user_help_message = '''Commands:
/selectgallery - select working gallery
/preview_month - show the selected month as preview of images
/download_month - download all photos of the selected month

To save an image just send it to me as document.'''