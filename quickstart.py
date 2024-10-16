from __future__ import print_function
import shutil
import cv2
import httplib2
import os
import os.path
import io
import zipfile

from File_work import Launch
import pymysql.cursors
import datetime
import time
import sys

from File_work import *  ## Исспользуются переменные:

thread = 0
######
###### command_num - колличество команд.
######
from Sof_to_FPGA import *  ## Исспользуются переменные:
def write_file(data, filename):
    with open(filename, 'wb') as f:
        f.write(data)
    return 'OK'

def file_delliter(file_id, service):
    try:
        service.files().delete(fileId=file_id).execute()
    except:
        print('Ошибка: файла не существует')

def CAD_LOOP():
    path = sys.argv[0]
    path_len = len(path.split('/')) - 1
    new_path = path.split('/')[:-1]
    new_str_path = "/".join(new_path)
    print(new_str_path)

    root_path = new_str_path

    student_zip = root_path+"/student_zip"
    print(student_zip)
    for root, dirs, files in os.walk(student_zip):  # В цикле проходим все папки и файлы в корневой папке
        for dir in dirs:
            dirpath = root + '/' + dir  # Добавляем в путь папки и необходимый файл
            shutil.rmtree(dirpath)
    for dirs in os.walk(root_path):
        if (dirs != "Archived") and (not(os.path.exists(root_path + "/Archived"))):
            os.mkdir(root_path + "/Archived")
        elif (dirs  != "Archive") and (not(os.path.exists(root_path + "/Archive"))):
            os.mkdir(root_path + "/Archive")
        elif (dirs != "video") and (not(os.path.exists(root_path + "/video"))):
            os.mkdir(root_path + "/video")


    config = configparser.ConfigParser()
    config_dir = root_path + '/' + "Config.ini"
    config.read(config_dir)
    config_path = config['Direc']['path']
    GLOBAL_PC_ID = config['PC']['id']
    if config_path == root_path:
        print("Путь к папке проекта существует")
    else:
        config['Direc']['path'] = root_path
        with open('Config.ini', 'w') as configfile:
            config.write(configfile)
        print("Путь до текущей директории был изменен")

    print("Root_path = ", root_path)

    launch_stat, pr_type, command_num, URL, errors_ = Launch(User_path_to_file=path_firmware, root_path=root_path)
    print("LAUNCH_STAT = ", launch_stat)
    time.sleep(60)

if __name__ == '__main__':
