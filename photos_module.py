import cv2
import os
import numpy as np
from PIL import Image
from datetime import datetime
import subprocess
import face_recognition
import numpy

SQUARE_IMG_SIZE        = 512
WHITE_BORDER_SIZE      = 0.5 #in percents
MAX_PREVIEW_TABLE_ROWS = 5

def create_preview(path, image_id, use_blackpage=True): 
    img = cv2.imread(path)

    if(img.shape[1] >= img.shape[0]):
        change_val = int((img.shape[1]-img.shape[0])/2)
        if(use_blackpage): img = cv2.copyMakeBorder(img, top=change_val, bottom=change_val, left=0, right=0, borderType=cv2.BORDER_CONSTANT, value=[0, 0, 0])
        else: img = img[0:img.shape[0], change_val:change_val+img.shape[0]]
    else:
        change_val = int((img.shape[0]-img.shape[1])/2)
        if(use_blackpage): img = cv2.copyMakeBorder(img, top=0, bottom=0, left=change_val, right=change_val, borderType=cv2.BORDER_CONSTANT, value=[0, 0, 0])
        else: img = img[change_val:change_val+img.shape[0], 0:img.shape[0]]
    outline_size = int(img.shape[0]/100*WHITE_BORDER_SIZE)
    img = cv2.copyMakeBorder(img, top=outline_size, bottom=outline_size, left=outline_size, right=outline_size, borderType=cv2.BORDER_CONSTANT, value=[255, 255, 255])
    img = cv2.resize(img, (SQUARE_IMG_SIZE, SQUARE_IMG_SIZE))

    size, baseline = cv2.getTextSize(str(image_id), cv2.FONT_HERSHEY_COMPLEX, fontScale=1, thickness=4)
    cv2.putText(img, text=str(image_id), org=(img.shape[0]-size[0]-baseline, img.shape[1]-size[1]),
        fontFace=cv2.FONT_HERSHEY_COMPLEX , fontScale=1, color=[0, 0, 0], lineType=cv2.LINE_AA, thickness=4)
    cv2.putText(img, text=str(image_id), org=(img.shape[0]-size[0]-baseline, img.shape[1]-size[1]),
        fontFace=cv2.FONT_HERSHEY_COMPLEX , fontScale=1, color=[255, 255, 255], lineType=cv2.LINE_AA, thickness=2)

    splitted_filename = os.path.splitext(path)
    filename = splitted_filename[0]+"_thumb"+splitted_filename[1]
    cv2.imwrite(filename, img)

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
    #append black square if last row has not enough pictures
    if(row[-1].shape[1] < SQUARE_IMG_SIZE*columns): rows[-1] = cv2.copyMakeBorder(rows[-1], top=0, bottom=0, left=0, right=(SQUARE_IMG_SIZE*columns - rows[-1].shape[1]), borderType=cv2.BORDER_CONSTANT, value=[0, 0, 0])
    print(len(rows))
    output = []
    if(len(rows) <= MAX_PREVIEW_TABLE_ROWS):
        table = rows[0]
        for row_i in range(1, len(rows)):
            table = np.concatenate((table, rows[row_i]), axis=0)
        output.append(cv2.imencode('.jpg', table)[1])
    else:
        for row_i in range(0, len(rows)):
            if(row_i % 10 == 0): table = rows[row_i]                    #start new table
            else: table = np.concatenate((table, rows[row_i]), axis=0)  #append to table

            if((row_i+1) % 10 == 0):                                      #throw to output every 10 rows
                output.append(cv2.imencode('.jpg', table)[1])
            elif(row_i == len(rows)-1):                                 #throw to output on last row
                output.append(cv2.imencode('.jpg', table)[1])

    return output

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

def heic_to_jpg(filename):
    #requires Imagemagick, but there are no other ways to keep EXIF
    subprocess.run(["convert", "%s" % filename, "%s" % (filename[0:-5] + '.jpg')])

#uses face detection
#if faces not found returns None
#if the number of found faces in different rotations are equal returns None
#in other cases returns values: 0 - 0deg, 1 - 90deg(ccw), 2 - 180deg, 3 - 90deg(cw)
def detect_rotation(path, number_of_times_to_upsample=2):
    img = face_recognition.load_image_file(path)
    faces = []
    faces.append(len(face_recognition.face_locations(img, number_of_times_to_upsample=number_of_times_to_upsample)))
    img = numpy.rot90(img)
    faces.append(len(face_recognition.face_locations(img, number_of_times_to_upsample=number_of_times_to_upsample)))
    img = numpy.rot90(img)
    faces.append(len(face_recognition.face_locations(img, number_of_times_to_upsample=number_of_times_to_upsample)))
    img = numpy.rot90(img)
    faces.append(len(face_recognition.face_locations(img, number_of_times_to_upsample=number_of_times_to_upsample)))
    print(faces)
    if(max(faces) == 0): return None
    elif(faces.count(max(faces)) != 1): return None
    else:
        return faces.index(max(faces))