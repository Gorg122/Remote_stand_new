import subprocess
import configparser
import serial.tools.list_ports
import sys

def Board_search():
    global proseed_flag

    root_path = "C:/Project_930/Project_main"
    config = configparser.ConfigParser()
    config_path = root_path + '/' + "Config.ini"
    config.read(config_path)
    Quartus_pgm_path = config['Quartus']['quartus_pgm_path']
    Arduino_name = config['Arduino']['arduino_name']
    if os.path.exists(Quartus_pgm_path):  # Проверяем существует ли данный путь исполняемых файлов
        Quartus_pgm_path = Quartus_pgm_path

        # В случае если такого пути нет, производим поиск пути исполняемых файлов в корневой папке
    else:
        find_in = "C:/intelFPGA_lite"  # Задаем корневую папку
        name = "quartus_pgm.exe"
        for root, dirs, files in os.walk(find_in):  # В цикле проходим все папки и файлы в корневой папке
            if name in files:
                Quartus_pgm_path = os.path.join(root, name)  # Добавляем в путь папки и необходимый файл
                # Обновляем в файле настроек путь до quartus_pgm.exe
                config['Quartus']['quartus_pgm_path'] = Quartus_pgm_path
                with open('Config.ini', 'w') as configfile:
                    config.write(configfile)

    curent_FPGA = subprocess.run(Quartus_pgm_path + " -l", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,
                                 text=True)
    cur_dev = curent_FPGA.stdout.rsplit('Info: ***************', 2)[0]
    print(cur_dev, "\n")
    # p.device
    for p in serial.tools.list_ports.comports():
        print(p)
        p = str(p)

    int1 = 1
    Arduino_port = "COM0"
    for p in serial.tools.list_ports.comports():
        if Arduino_name in p.description:
            while int1 < 9:  # В цикле проходим порты от "COM0" до "COM8".

                if Arduino_name in p[1]:  # Ищем подходящее название Arduino в p[1].
                    str2 = str(int1)  # Конвертируем номер порта из int в str:
                    Arduino_port = "COM" + str2  # Соединяем номер порта с его названием.

                # Ещё раз ищем название платы Arduino и номер COM порта"
                if Arduino_name in p[1] and Arduino_port in p[1]:
                    # print ("Найдена  " + Arduino_name + Arduino_port + "\n")
                    int1 = 9  # Выходим из цикла.

                if int1 == 8:
                    # print ("Плата не найдена")
                    sys.exit()  # Прекращение выполнения скрипта.

                int1 = int1 + 1
    print(Arduino_port)
    #Arduino_port = arduino_port.split()
    return Arduino_port
