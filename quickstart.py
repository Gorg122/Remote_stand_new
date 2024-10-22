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



def CAD_LOOP(path_firmware, script_file_path):
    path = sys.argv[0]
    new_path = path.split('/')[:-1]
    new_str_path = "/".join(new_path)
    root_path = new_str_path

    # for dirs in os.walk(root_path):
    #     if (dirs != "Archived") and (not(os.path.exists(root_path + "/Archived"))):
    #         os.mkdir(root_path + "/Archived")
    #     elif (dirs != "Archive") and (not(os.path.exists(root_path + "/Archive"))):
    #         os.mkdir(root_path + "/Archive")
    #     elif (dirs != "video") and (not(os.path.exists(root_path + "/video"))):
    #         os.mkdir(root_path + "/video")

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

    launch_stat, pr_type, command_num, errors_ = Launch(
        sof_file_path=path_firmware,
        script_file_path=script_file_path,
        root_path=root_path)
    print("LAUNCH_STAT = ", launch_stat)


if __name__ == '__main__':
    CAD_LOOP(path_firmware='Firmware.sof', script_file_path='Script.txt')
