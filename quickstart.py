from __future__ import print_function
import shutil
import cv2
import os

from File_work import Launch
import datetime
import time
import sys

from File_work import *  ## Исспользуются переменные:

thread = 0

def CAD_LOOP(path_firmware, script_file_path):
    path = sys.argv[0]
    new_path = path.split('/')[:-1]
    new_str_path = "/".join(new_path)
    root_path = new_str_path

    #print("root_path = ", root_path)
    root_path = "C:/Kirill_Stand_New/From_stand/Remote_stand_new"
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
