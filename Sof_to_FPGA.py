import os.path
import subprocess
import configparser
global pr_type
pr_type = 2

def FPGA_flash(User_path, sof_file_path , FPGA_num, root_path):
    global pr_type
    # Задаем ключ успешной прошивки платы
    main_key = ["Quartus Prime Programmer was successful. 0 errors"]

    # Обращаемся к файлу настроек
    config = configparser.ConfigParser()
    config_path = root_path + '/' + "Config.ini"
    config.read(config_path)

    # Задаем директории исполняемых файлов quartus
    Quartus_pgm_path = config['Quartus']['quartus_pgm_path']
    #Quartus_sh_path = config['Quartus']['quartus_sh_path']
    root_directory = config['Direc']['Path']

    # Задаем заглушки путей к основным файлам
    qpf_path = "Not_yet"
    qsf_path = "Not_yet"
    sof_path = "Not_yet"

    # Создаем файл отчета о прошивке платы ПЛИС
    log_file = open(root_directory + '/' + User_path + "/JTAG_config.txt", "w")

    # Проверка существования пути к quartus_pgm.exe
    if os.path.exists(Quartus_pgm_path):  # Проверяем существует ли данный путь исполняемых файлов
        Quartus_pgm_path = Quartus_pgm_path

    # В случае если такого пути нет, производим поиск пути исполняемых файлов в корневой папке
    else:
        raise IOError("Путь Quartus_pgm_path не существует")

    # Если файл прошивки существует, начинаем поиск подключенной платы ПЛИС
    if os.path.exists(sof_file_path):
        print("Выводим список подключенных устройств")
        # Выводим список всех подключенных плат средствами quartus_pgm.exe
        curent_FPGA = subprocess.run(Quartus_pgm_path + " -l", stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     shell=True, text=True)
        print("Curent_fpga = ", curent_FPGA, "\n")
        # print(curent_FPGA.returncode,"\n") # флаг успешного выполнения команды
        # print(curent_FPGA.stdout,"\n") # Вывод консоли
        fpga_list = curent_FPGA.stdout.split("Info: Processing started:", 2)[0]

        if not curent_FPGA:
            raise IOError("Плата ПЛИС не найдена")


        # Получаем номер той платы, которую в данный момент необходимо прошивать
        FPGA_num = FPGA_num
        str = "{}) ".format(FPGA_num)
        # В случае, если плата с заданным номером существует, определяем порт её подключения как основной
        if curent_FPGA.stdout.find(str) != -1:
            curent_port = curent_FPGA.stdout.split(str, 2)[1]
            curent_port = curent_port.split('\n', 1)[0]
            print("curent port = ", curent_port)

        # Если такой платы не существует, выводим соответствую ошибку
        else:
            raise IOError("Плата ПЛИС с заданным индексом не найдена")


        # Выводим список устроств, подключенных к данному порту платы
        modules_FPGA = subprocess.run("{0} -c \"{1}\" -a".format(Quartus_pgm_path, curent_port), stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, shell=True, text=True)
        #i = 0

        # Отделяем от всего вывода консоли информацию о подключенных устроствах
        cur_dev = modules_FPGA.stdout.rsplit('Info: ***************', 2)[0]
        device_numbers = cur_dev.split('\n')
        print("device_numbers = ", device_numbers)
        # В случае, если плата ПЛИс имеет более 1 ядра
        if len(device_numbers) > 4:
            #curent_device = modules_FPGA.stdout.split('\n', 3)[2]
            #################### Обратить внимание при использовании DE10-NANO ##########################
            #curent_device = str(curent_device[12:36])

            #print("Текущая плата =", curent_device)
            #print("Несколько ядер")
            # Производим прошивку необходимого ядра платы ПЛИС
            i = 2
            result = subprocess.run(
                '{0} -m JTAG -c "{1}" -o p;{2}@{3}'.format(Quartus_pgm_path, curent_port, sof_path, i),
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
            fpga_flashed = result.stdout.split("Info: Processing started:", 2)[1]
            print(fpga_flashed, '\n')  # Вывод консоли
            # Записываем вывод консоли в файл отчета о прошивке платы ПЛИС
            log_file.write(fpga_flashed)
            log_file.close()
            # Обрабатываем 2 состояния завершения прошивки платы
            if result.stdout.count(main_key[0]):
                print("Прошивка платы ПЛИС окончена")
                return ("OK", pr_type)
            else:
                print("Прошивка платы ПЛИС заверщилась неудачей")
                return ("Neok")


        # Если плата ПЛИС имеет одно ядро
        else:
            print("Плата ПЛИС имеет одно ядро\n")
            print(sof_path, "\n")
            # Производим прошивку платы ПЛИС без указания ядра назначения
            result = subprocess.run('{0} -m JTAG -c "{1}" -o p;{2}'.format(Quartus_pgm_path, curent_port, sof_path),
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,
                                    text=True)
            print("###############################################")
            print(result.stdout)
            print("##################################")
            try:
                fpga_flashed = result.stdout.split("Info: Processing started:", 2)[1]
                print(fpga_flashed, '\n')  # Вывод консоли
            except:
                fpga_flashed = "Ошибка при прошивке платы ПЛИС"
            print("FPGA FLASHED = ", fpga_flashed)
            # Записываем вывод консоли в файл отчета о прошивке платы ПЛИС
            log_file.write(fpga_flashed)
            log_file.close()
            # print(result.stdout,'\n') # Вывод консоли

            # Обрабатываем 2 состояния завершения прошивки платы
            if result.stdout.count(main_key[0]):
                print("Прошивка платы ПЛИС окончена")
                return ("OK", pr_type)
            else:
                return ("Прошить плату не удалось", pr_type)

#FPGA_flash(User_path = "student_zip/petukhov", sof_file_path = "C:/Kirill_Stand_New/From_stand/Remote_stand_new/student_zip/petukhov/Firmware.sof" , root_path = "C:/Kirill_Stand_New/From_stand/Remote_stand_new", FPGA_num = 1)
