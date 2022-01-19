print("Starting...")
import cv2
import os
import photos_module

print("Opening...")
photos = [photos_module.open_photo("Library/1.jpg"), photos_module.open_photo("Library/2.jpg"), photos_module.open_photo("Library/3.jpg"), photos_module.open_photo("Library/4.jpg"), photos_module.open_photo("Library/5.jpg"), photos_module.open_photo("Library/6.jpg"), photos_module.open_photo("Library/7.jpg"), photos_module.open_photo("Library/8.jpg")]

print("Working...")
for i in range(len(photos)):
	photos[i] = photos_module.crop_and_resize(photos[i], use_blackpage=True)

cv2.imshow("test", photos_module.create_preview_table(photos))
cv2.waitKey(0)