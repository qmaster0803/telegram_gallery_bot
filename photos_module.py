import cv2
import os
import numpy as np
from PIL import Image
from datetime import datetime

SQUARE_IMG_SIZE = 512
WHITE_BORDER_SIZE = 0.5 #in percents

def create_preview(path, use_blackpage=True): 
    img = cv2.imread(path)

    if(img.shape[1] >= img.shape[0]):
        change_val = int((img.shape[1]-img.shape[0])/2)
        if(use_blackpage): cropped = cv2.copyMakeBorder(img, top=change_val, bottom=change_val, left=0, right=0, borderType=cv2.BORDER_CONSTANT, value=[0, 0, 0])
        else: cropped = img[0:img.shape[0], change_val:change_val+img.shape[0]]
    else:
        change_val = int((img.shape[0]-img.shape[1])/2)
        if(use_blackpage): cropped = cv2.copyMakeBorder(img, top=0, bottom=0, left=change_val, right=change_val, borderType=cv2.BORDER_CONSTANT, value=[0, 0, 0])
        else: cropped = img[change_val:change_val+img.shape[0], 0:img.shape[0]]
    outline_size = int(cropped.shape[0]/100*WHITE_BORDER_SIZE)
    cropped = cv2.copyMakeBorder(cropped, top=outline_size, bottom=outline_size, left=outline_size, right=outline_size, borderType=cv2.BORDER_CONSTANT, value=[255, 255, 255])
    resized = cv2.resize(cropped, (SQUARE_IMG_SIZE, SQUARE_IMG_SIZE))

    splitted_filename = os.path.splitext(path)
    filename = splitted_filename[0]+"_thumb"+splitted_filename[1]
    cv2.imwrite(filename, resized)

def create_preview_table(img_paths, columns=3):
    imgs = []
    for path in img_paths:
        imgs.append(cv2.imread(path))
    rows = []
    i = 0
    while(True):
        if((i+1)%columns == 1 and i != len(imgs)):
            if(i != 0): rows.append(row)
            row = imgs[i]
        elif(i != len(imgs)): row = np.concatenate((row, imgs[i]), axis=1)
        else:
            rows.append(row)
            break
        i += 1
    output = rows[0]
    if(row[-1].shape[1] < SQUARE_IMG_SIZE*columns): rows[-1] = cv2.copyMakeBorder(rows[-1], top=0, bottom=0, left=0, right=(SQUARE_IMG_SIZE*columns - rows[-1].shape[1]), borderType=cv2.BORDER_CONSTANT, value=[0, 0, 0])
    for row_i in range(1, len(rows)):
        output = np.concatenate((output, rows[row_i]), axis=0)
    return cv2.imencode('.jpg', output)[1]

def open_photo(path):
    return cv2.imread(path)

def get_photo_date(path):
    img = Image.open(path)
    exif = img.getexif()
    creation_time = exif.get(36867)
    #according to EXIF docs, datetime format is "YYYY:MM:DD HH:MM:SS"
    if(creation_time != None):
        timestamp = datetime.timestamp(datetime.strptime(creation_time, "%Y:%m:%d %H:%M:%S"))
        return int(timestamp)
    else:
        return None