import os
import shutil
import re
import time
import serial
import sys
import subprocess
import configparser
import pprint
from datetime import date
from dateutil import parser



from Sof_to_FPGA import FPGA_flash
from Find_arduino import Find_Arduino

# Счетчик комманд пользователя
global command_num
command_num = -1
global pr_type
pr_type = 2

    # Обработка случая отсутствия файла сценария, или возврат имени файла и пути к нему
    # if not os.path.exists(script_file_path):
    #     errors_file.write("Отсутствует файл сценария\n")
    #     errors_file.close()
    #     return ("Neok", "Neok")
    # else:
    #     errors_file.close()
    #     return (script_file_path, script_file_name)


# Словарь текущих состояний переключателей
switches = dict([(1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0)])


# Скрипт передачи управляющих команд на плату Ардуино
def Serial_delivery(arduino, cur_action, curent_pin, sleep, sleep_dur):
    global switches
    # Распознаем текущую команду
    if cur_action:
        try:
            # Проверяем текущее состояние переключателя
            print("Curent_pin = ", curent_pin)
            print("Curent_pin_status = ", switches[int(curent_pin)])
            if switches[int(curent_pin)] == 0:
                comand_sw1 = str(curent_pin) + "H"
                arduino.write(bytes(comand_sw1, 'utf-8'))
                print("SW - {} - H".format(curent_pin))
                switches[int(curent_pin)] = 1

            else:  # switches[int(curent_pin)] == 1:
                comand_sw2 = str(curent_pin) + "L"
                print("SW - {} - L".format(curent_pin))
                arduino.write(bytes(comand_sw2, 'utf-8'))
                switches[int(curent_pin)] = 0
            # arduino.write(bytes(comand_sw1, 'utf-8'))
            time.sleep(1)
            # Получаем ответ от платы Ардуино об удачной отправке данного сигнала
            data = str(arduino.readline().decode().strip('\r\n'))
            time.sleep(1)
            print(data, '\n')

            # Изменяем состояние данного переключателя в словаре на текущее
            if sleep:
                print("sleep for ", sleep_dur)
                time.sleep(sleep_dur)
                print("sleep is over")

        except:
            print("Неверно указанный пин переключателя  ")
    else:
        try:
            comand_but1 = str(curent_pin) + "H"
            arduino.write(bytes(comand_but1, 'utf-8'))
            print("BT - {} - H".format(curent_pin))
            time.sleep(1)
            # Получаем ответ от платы Ардуино об удачной отправке данного сигнала
            data = str(arduino.readline().decode().strip('\r\n'))
            time.sleep(1)
            print(data, '\n')


            comand_but2 = str(curent_pin) + "L"
            arduino.write(bytes(comand_but2, 'utf-8'))
            print("BT - {} - L".format(curent_pin))
            time.sleep(1)
            # Получаем ответ от платы Ардуино об удачной отправке данного сигнала
            data = str(arduino.readline().decode().strip('\r\n'))
            time.sleep(1)
            print(data, '\n')

            # Запускаем процесс ожидания задержки, указанной пользователем
            if sleep:
                print("sleep for ", sleep_dur)

                time.sleep(sleep_dur)
                print("sleep is over")


                # Передаем сигнал о необходимости перевести в неактивное положение необходимую кнопку
                comand_but2 = str(curent_pin) + "L"
                arduino.write(bytes(comand_but2, 'utf-8'))
                print("BT - {} - L".format(curent_pin))
                time.sleep(1)
                # Получаем ответ от платы Ардуино об удачной отправке данного сигнала
                data = str(arduino.readline().decode().strip('\r\n'))
                time.sleep(1)
                print(data, '\n')

        except:
            print("Неверно указан номер кнопки")
    return switches


def Arduino_Serial(script_file_path, errs_path, Arduino_port):
    # Открываем файл сценария
    input_file = open(script_file_path)

    config = configparser.ConfigParser()
    config.read("Config.ini")

    print(len(re.findall(r"[\n']+?", open(script_file_path).read())))
    all_strings = len(re.findall(r"[\n']+?", open(script_file_path).read()))

    # Выведем количество без пустых строк
    print(len(re.findall(r"[\n']+", open(script_file_path).read())))
    strings = len(re.findall(r"[\n']+", open(script_file_path).read()))

    time.sleep(1)

    # Открываем файл текущими ошибками в файле скрипта
    errors_file = open(errs_path, "w")

    # Построчно читаем файл сценария
    lines = input_file.readlines()

    # Задаем основные переменные для распознавания файла сценария
    but = ["button", "but", "But", "Button"]
    sw = ["switch", "sw", "Switch", "Sw"]
    end = ["end"]
    delay = ["delay"]
    # start = ["ardok"]
    start = config['Arduino']['arduino_key']
    current_commands = 0

    # Подключаемся к плату Ардуино через последовательный порт, к заранее определенному COM порту
    arduino = serial.Serial(port=Arduino_port, baudrate=9600, timeout=.1)
    y = 0
    # Ожидаем успешного подключения
    time.sleep(3)

    # Отправляем контрольную последовательность и ожидаем положительного ответа
    while y != 1:
        poslanie = "Hello"
        print("Подключение к плате Ардуино")
        arduino.write(bytes(poslanie, 'utf-8'))
        data = str(arduino.readline().decode().strip('\r\n'))
        if str(data).count(start[0]):
            print("Контрольная последовательность получена")
            y += 1

    # Начало передачи управляющих сигналов на плату Ардуино
    print("Начало передачи сигналов")
    # Выполняем проходку по непустым строкам файла сценария
    for i in range(strings):
        wrong_delay = 0
        end_of_file = 0
        now_slip = 1
        sleep_dur = 0
        # Поиск численного значения в строке
        num = re.findall(r'\d+', str(lines[i]))
        false_pin = False
        cur_action = 2
        sleep = 0

        # Собираем число из списка отдельных чисел в строке
        for item in num:
            numbers = int(item)

        # Определяем текущее действие (нажаите кнопки или нажатие переключателя)
        for j in range(len(but)):
            if (lines[i].count(but[j])):
                cur_action = 0  # Текущей командой является нажатие кнопки
            elif (lines[i].count(sw[j])):
                cur_action = 1  # Текущеу командой является переключение переключателя
        if (lines[i].count(end[0])):
            end_of_file = 1
        # Определяем наличие задержки по времени к данному действию
        if not (end_of_file):
            if (lines[i + 1].count(delay[0])) and (cur_action != 2):
                sleep = 1
                sleep_num = re.findall(r'\d+', str(lines[i + 1]))
                for item in sleep_num:
                    sleep_dur += int(item)
                # Обработка ошибки слишком большой длительности записи видео (с указанием конкретной строки)
                if sleep_dur > 30:
                    delay_string = i + 1
                    wrong_delay = 1
                    errors_file.write("Длительность задержки не больше 30 секунд (строка: " + str(delay_string) + ")\n")

        # В случае, если строка не пустая, определяем верно ли указаны номера кнопок и переключателей
        if lines[i] != "\n" and lines[i] != "":
            print(numbers)
            # if (sleep != 1) and (cur_action != 2):

            # Если номер кнопки или переключателя больше 8 или меньше 1, данная команда не обрабатывается
            if ((int(numbers) > 8) or (int(numbers) < 1)) and (now_slip != 1):

                false_pin = True
                print("Указан неверный пин")
                if int(numbers) > 7:
                    errors_file.write("Указан пин большей разрядности (строка " + str(i) + ")\n")
                elif int(numbers) < 0:
                    errors_file.write("Указан пин меньшей разрядности (строка " + str(i) + ")\n")
                i += 1
                # Запись ошибки невверно указанного номера пина (с указанием конкретной строки)
                # errors_file.write("Количество активных пинов равно 8 (строка " + str(i) + ")\n")
                # print("Неверно указан номер пина\n")
                # GUI.print_log("Неправильно указан номер пина")
        # Если строка пустая, пропускаем её
        if (lines[i] == "\n" and not (lines[i + 1].count(end[0]))):
            i += 1
        # В случае, если номер пина введен верно, и строка не является пустой, начинаем обработку команды
        elif (false_pin == False):
            # Обработка команд управления
            # Обработка нажатия переключателя
            if (cur_action == 1):
                # Проверяем данную команду на предмет установленных задержек
                if (sleep) and (not (wrong_delay)):
                    # Запускаем функцию передачи управляющего сигнала на плату Arduino
                    switches = Serial_delivery(arduino, 1, num[0], 1, sleep_dur)
                    current_commands += 1
                    i += 1
                    num[0] = 0
                if not (lines[i].count(delay[0])):
                    switches = Serial_delivery(arduino, 1, num[0], 0, 0)
                    current_commands += 1

            # Обработка нажатия кнопки
            elif (cur_action == 0):
                # Проверяем данную команду на предмет установленных задержек
                if sleep and (not (wrong_delay)):
                    switches = Serial_delivery(arduino, 0, num[0], 1, sleep_dur)
                    current_commands += 1
                else:
                    switches = Serial_delivery(arduino, 0, num[0], 0, 0)
                    current_commands += 1

            # Определяем ключ окончания обработки файла сценария
            if (lines[i].count(end[0])):
                print(switches)
                # Закрываем файл сценария пользователя
                input_file.close()
                # Выводим итоговое количество команд в файле сценария
                break
    # Закрываем файл ошибок, и ещё раз закрываем файл сценария
    input_file.close()
    errors_file.close()
    print("Total_commands = ", current_commands)
    # = current_commands
    return ("Ok", current_commands)


# Функция проверки на пустые файлы
def File_empty_chek(users_dir, file_name):
    chek_file = ""
    for files in os.listdir(users_dir):
        if files.find(file_name) != -1:
            print("path = ", users_dir)
            print(files)
            file_r = open(users_dir + '/' + files)
            # Записываем из файла первые 2 символа
            chek_file = file_r.read(2)
            file_name = files
            file_r.close()
            # print(chek_file, '\n')
    return chek_file, file_name


# Функция копирования и удаления основных файлов пользователя после завершения процесса обработки сценария
def File_switch(root_path, sof_path, script_file_path, sof_file_name, script_file_name,
                video_return):
    # Формируем переменную пути по текущей папке пользвоателя
    dest_dir = root_path + '/result'

    # Изменяем текущую директорию на директорию пользователя

    # Задаем стоковые значения файлов
    chek_errors_file = ""
    chek_compil_file = ""
    chek_JTAG_file = ""
    log_name = "@"
    er_name = "$"
    config_file = "!"

    # Читаем каждый файл и записываем их данные в отдельную переменную
    chek_errors_file, er_name = File_empty_chek(dest_dir, 'errors.txt')
    #chek_compil_file, log_name = File_empty_chek(dest_dir, 'Proj_compil_result.txt')
    #chek_JTAG_file, config_file = File_empty_chek(dest_dir, 'JTAG_config.txt')

    # Создаем переменные путей к файлам ошибок, отчета компиляции, и отчета прошивки платы ПЛИС
    errs_file_path = dest_dir + "/" + er_name
    compil_path = dest_dir + "/" + log_name
    config_path = dest_dir + "/" + config_file

    # Если файлы пустые, удаляем их
    if chek_errors_file == "" and os.path.exists(errs_file_path):
        os.remove(errs_file_path)

    # if chek_compil_file == "" and os.path.exists(compil_path):
    #     os.remove(compil_path)

    if chek_JTAG_file == "" and os.path.exists(config_path):
        os.remove(config_path)

    # Создаем конечную папку пользователя, если её не существует
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)

    # Перемещение файлов в конечную папку пользователя
    print("File with errors = " + er_name)
    er_name = "".join(er_name)
    if os.path.exists(errs_file_path):
        print("Перенос файла ошибок\n")
        shutil.copy(errs_file_path, dest_dir + "/" + er_name)
        time.sleep(1)
        os.remove(errs_file_path)

    # print("File_compil = " + log_name)
    # if os.path.exists(compil_path):
    #     print("Перенос файла отчета компиляции\n")
    #     shutil.copy(compil_path, dest_dir + "/" + log_name)
    #     time.sleep(1)
    #     os.remove(compil_path)

    print("Config file = " + config_file)
    if os.path.exists(config_path):
        print("Перенос файла отчета прошивки\n")
        shutil.copy(config_path, dest_dir + "/" + config_file)
        time.sleep(1)
        os.remove(config_path)

    print("TXT_script_file = ", script_file_path)
    print(script_file_path, '\n')
    if os.path.exists(script_file_path):
        print("Перенос файла сценария\n")
        shutil.copy(script_file_path, dest_dir + "/" + script_file_name)
        time.sleep(1)
        os.remove(script_file_path)

    print("SOF_FILE = ", sof_path)
    print(sof_path, '\n')
    if os.path.exists(sof_path):
        print("Перенос файла прошивки\n")
        shutil.copy(sof_path, dest_dir + "/" + sof_file_name)
        time.sleep(3)
        os.remove(sof_path)

    i = 0
    video_path = root_path + "/video/video.mp4"
    copy_dst = dest_dir + "/video.mp4"
    vid_exists = True
    # Производим проверку окончания записи видео
    while vid_exists:
        print(video_return)
        # Проверяем существует ли видео, и файл окончания записи видео
        if os.path.exists(video_path) and os.path.exists(root_path + "/video_done.txt"):
            print("Видео записано", '\n')
            time.sleep(5)

            # Проивзодим копирование видео в конечную папку пользвоателя
            copy_chek = copy_with_progress(src=video_path, dst=copy_dst)

            # После возврата флага окончания копирования, удаляем видео в первоначальной папке
            if copy_chek == "OK":
                print("\n")
                print("Видео удаляется")
                os.remove(video_path)
            time.sleep(2)

            # Если видео найдено выходим из цикла проверка на существование видео
            vid_exists = False
        # Иначе запускаем счетчик ожидания нахождения файла видеозаписи
        elif i == 20:
            # print(i)
            # В случае, если видео не найдено, выводим соответствующее сообщение
            print("Видео нет")
            # Если видео не найдено выходим из цикла проверка на существование видео
            vid_exists = False

        else:
            i += 1
    return "OK"


# Функция удаления ненужных файлов после окончания обработки прошивки пользователя

# def Files_to_archive(path_to_dir, user_name, for_delivery, users_dir):
#     new_path = path_to_dir + '/' + user_name
#     # В случае если папка копирования существует, создаем в ней архив с файлами
#     if os.path.exists(new_path):
#         shutil.rmtree(new_path)
#         os.makedirs(new_path)
#         os.chdir(new_path)
#         shutil.make_archive("result", 'zip', users_dir)
#         if for_delivery:
#             folder_send = "" + new_path
#             return folder_send
#     # В случае, если папка пользователя не существует, создаем ее и архив файлов
#     else:
#         os.makedirs(new_path)
#         os.chdir(new_path)
#         shutil.make_archive("result", 'zip', users_dir)


def Delete_files(root_path):
    #users_dir = root_path + '/' + User_path_to_file
    # Производим поиск файла окончания процесса записи видео
    if os.path.exists(root_path + "/video_done.txt") \
            and os.path.isfile(root_path + "/video_done.txt"):
        print("Удаление файла video_done.txt\n")
        # Удаляем данный файл
        os.remove(root_path + "/video_done.txt")

    # Производим поиск файла, содержащего длительность записи видео
    if os.path.exists(root_path + "/video_timing.txt") \
            and os.path.isfile(root_path + "/video_timing.txt"):
        print("Удаление файла video_timing.txt\n")
        # Удаляем данный файл
        os.remove(root_path + "/video_timing.txt")

    # Задаем папки сохранения архивных записей, а также папку для отправки ответов пользователю
    # new_users_dir = root_path + "/Archived"
    # archive_dir = root_path + "/Archive"
    # os.chdir(new_users_dir)
    #
    # # Создаем архив файлов на отправку
    # result_directory = User_path_to_file.split('/', 2)[1]
    # print("Создание архива на отправку")
    # folder_send = Files_to_archive(new_users_dir, result_directory, 1, users_dir)
    # print("Архив на отправку создан")
    #
    # # Создаем архив файлов в хранилище
    # print("Создание архива в хранилище/n")
    # Files_to_archive(archive_dir, result_directory, 0, users_dir)
    # print("Архив в хранилище создан/n")
    return "Ok"


# Функция добавления прогресс-бара
def progress_percentage(perc, width=None):
    # Задаем цвет прогресс-бара
    FULL_BLOCK = '█'
    # Градиент, сигнализирующий о процессе выполнения
    INCOMPLETE_BLOCK_GRAD = ['░', '▒', '▓']

    assert (isinstance(perc, float))
    assert (0. <= perc <= 100.)
    # Если ширина прогресс-бара не задана
    if width is None:
        width = os.get_terminal_size().columns
    # Прогресс бар - это блочный виджет, perc_widget является разделителем
    max_perc_widget = '[100.00%]'  # 100% это максимальное значение
    separator = ' '
    blocks_widget_width = width - len(separator) - len(max_perc_widget)
    assert (blocks_widget_width >= 10)  # Не очень важно, если это не так
    perc_per_block = 100.0 / blocks_widget_width
    # epsilon - это чувствительность градиента цвета блока выполнения
    epsilon = 1e-6
    # Количество блоков, работа над которыми выполнена
    full_blocks = int((perc + epsilon) / perc_per_block)
    # Остальные блоки считаются невыполненными
    empty_blocks = blocks_widget_width - full_blocks

    # Формируем виджет
    blocks_widget = ([FULL_BLOCK] * full_blocks)
    blocks_widget.extend([INCOMPLETE_BLOCK_GRAD[0]] * empty_blocks)
    # remainder - насколько наши блоки разбиты частей
    remainder = perc - full_blocks * perc_per_block
    # epsilon необходима для поиска ошибок (должна быть != 0.)
    # Основываясь на reminder задаем первичный окрас
    # Зависит от remainder
    if remainder > epsilon:
        grad_index = int((len(INCOMPLETE_BLOCK_GRAD) * remainder) / perc_per_block)
        blocks_widget[full_blocks] = INCOMPLETE_BLOCK_GRAD[grad_index]

    # Формируем виджет демонстрации процента выполнения
    str_perc = '%.2f' % perc
    perc_widget = '[%s%%]' % str_perc.ljust(len(max_perc_widget) - 3)

    # Формируем прогресс-бар
    progress_bar = '%s%s%s' % (''.join(blocks_widget), separator, perc_widget)
    # Возвращаем прогресс-бар в качестве строки
    return ''.join(progress_bar)


# Функция подсчета текущего процента выполнения
def copy_progress(copied, total):
    print('\r' + progress_percentage(100 * copied / total, width=30), end='')


# Функция копирования файла
def copyfile(src, dst, *, follow_symlinks=True):
    """Копирование данных из src в dst.

Если значение follow_symlinks не задано, а src является символической ссылкой,
вместо копирования файла, на который она указывает, будет создана новая символическая ссылка.

    """
    # Проверка на соответствие src и dst
    if shutil._samefile(src, dst):
        raise shutil.SameFileError("{!r} и {!r} являются одним и тем же файлом".format(src, dst))

    # Проходка по всем файлам в src и dst
    for fn in [src, dst]:
        try:
            st = os.stat(fn)
        except OSError:
            # Файл, скорее всего, не существует
            pass
        else:
            # Проверка на наличие других специфичных файлов
            if shutil.stat.S_ISFIFO(st.st_mode):
                raise shutil.SpecialFileError("`%s` является именованным каналом" % fn)

    # Проверка задана ли переменная follow_symlinks
    if not follow_symlinks and os.path.islink(src):
        os.symlink(os.readlink(src), dst)
    # Если переменная задана
    else:
        size = os.stat(src).st_size
        with open(src, 'rb') as fsrc:
            with open(dst, 'wb') as fdst:
                copyfileobj(fsrc, fdst, callback=copy_progress, total=size)
    return dst


def copyfileobj(fsrc, fdst, callback, total, length=16 * 1024):
    copied = 0
    while True:
        buf = fsrc.read(length)
        if not buf:
            break
        fdst.write(buf)
        copied += len(buf)
        callback(copied, total=total)


# Функция копирования файлового объекта из src в dst
def copy_with_progress(src, dst, *, follow_symlinks=True):
    # Проверка является ли dst директорией
    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    # Вызываем функцию copyfile для выполнения копирования с ожиданием выполнения
    copyfile(src, dst, follow_symlinks=follow_symlinks)
    shutil.copymode(src, dst)
    return "OK"


# Главная функция обработки файлов пользователя
def Launch(script_file_path, sof_file_path,  root_path):
    global command_num
    global pr_type
    errors_ = 0
    # Перемещаемся в текущую папку проекта
    #os.chdir(root_path)

    # Открываем файл настроек
    config = configparser.ConfigParser()
    config_path = root_path + '/' + "Config.ini"
    config.read(config_path)

    # Выводим имеющиеся в файле конфигурации ключи
    # keys = config.keys()
    # for key in keys:
    #     print(config[key])

    # Читаем из файла конфигурации текущую папку проекта
    root_path = config['Direc']['Path']
    python_path = config['Python']['path']

    print(root_path)

    # Созщдаем и открываем файл ошибок
    errs_f = "errors.txt"

    errs_name = root_path + '/result'

    errs_path = errs_name + '/' + errs_f
    errors_file = open(errs_path, "w")
    delay = ["delay"]

    # Запускаем функцию поиска файла прошивки

    # ВАЖНОЕ МЕСТО //
    '''script_file_path, script_file_name = Script_file_detect(User_path_to_file=User_path_to_file,
                                                            root_path=root_path,
                                                            errs_path=errs_path)
    '''
    #script_file_path, script_file_name = "","" ТО ЧТО ПЕРЕДАЕТ КИРИЛЛ

    # Выводим результат выполнения данной функции
    print(script_file_path)
    # scetch_name = "scetch"
    User_path = 'result'
    # Если файл сценария существует
    if os.path.exists(script_file_path) and os.path.exists(sof_file_path):
        # Запускаем процесс обработки пользовательской прошивки
        # sof_path = "#"
        # sof_file_name = "#"
        # Запускаем функцию взаимодействия с платой Ардуино, выводим порт подключения
        Arduino_port = Find_Arduino(root_path=root_path)
        print(Arduino_port, '\n')
        print(Arduino_port[0:3], '\n')

        # Обрабатываем ошибку поиска порта подключения платы Ардуино
        if Arduino_port[0:3] != 'COM':
            errors_file.write("Проблема при передаче управляющих сигналов, свяжитесь с преподавателем\n")

        # Запускаем функцию взаимодействия с платой ПЛИС
        FPGA_chek, pr_type = FPGA_flash(User_path, sof_file_path, FPGA_num=1, root_path=root_path)
        # Производим обработку ошибок компиляции проекта или прошивки платы
        if FPGA_chek != "OK":
            returncode = 1
            errors_ = 1
            errors_file.write("Проблема с компиляцией проекта, или прошивкой платы, изучите файлы логов\n")

        # Производим поиск файла прошивки после окончания прошивки платы ПЛИС или компиляции проекта
        # for root, dirs, files in os.walk(root_path + '/' + sof_file_path):
        #     for file in files:
        #         if file.endswith(".sof"):
        #             sof_file_name = file
        #             sof_path = root + '/' + sof_file_name
        #
        #             print(sof_path)

        sof_path = sof_file_path
        # Маркер существования видеофайла
        vid_chek = "video_none"

        # Если файл прошивки существует, и работа с платой ПЛИС успешна, запускаем обработку прошивки пользователя
        if os.path.exists(sof_file_path) and FPGA_chek == "OK":

            # Открываем файл сценария
            input_file = open(script_file_path)

            # print(len(re.findall(r"[\n']+", open(script_file_path).read())))
            # Построчно читаем файл сценария
            lines = input_file.readlines()
            # Найдем количество не пустых строк в файле сценария
            strings = len(re.findall(r"[\n']+", open(script_file_path).read()))
            print("ВСЕГО НЕ ПУСТЫХ СТРОК = ", strings)
            sleep_timing = 0
            for i in range(strings):
                # Поиск указания временных задержек
                if lines[i].count(delay[0]):
                    # Поиск чисел в конкретной строке файла сценария
                    sleep_num = re.findall(r'\d+', str(lines[i]))
                    for item in sleep_num:
                        sleep_dur = int(item)
                    # Длительность единократной задержки не более 30 секунд
                    if sleep_dur > 30:
                        sleep_dur = 30
                    print("Очередной слип на", sleep_dur)
                    sleep_timing = sleep_timing + sleep_dur
            strings = strings

            # Выводим суммарные тайминги
            print("Время записи видео благодаря командам: ", strings)
            print("Суммарное время слипов: ", sleep_timing)
            strings = strings + sleep_timing
            # Длительностт видео не может быть больше 2 минут
            if strings > 120:
                strings = 120
            # Выводим суммарное время записи видео
            print("Суммарное время записи видео: ", strings)

            # Создаем файл временных параметров записи видео
            video_file = open("video_timing.txt", "w")
            # Записываем в данный файо необходимую длительность видео
            video_file.write(str(strings))
            video_file.close()
            input_file.close()
            time.sleep(1)

            # Запускаем функцию записи видео
            video_script_path = root_path + '/' + "Video.py"
            # python_path = "C:/Users/grish/AppData/Local/Programs/Python/Python38/python.exe"
            print("---------------------------------------------------------------------------------------------------")
            print("PYTHON _PATH = ", python_path)
            print("VIDEO_SCRIPT_PATH = ", video_script_path)
            print("---------------------------------------------------------------------------------------------------")
            Video_chek = subprocess.Popen([python_path, video_script_path])

            # Запускаем функцию последовательной передачи управляющих команд на плату Ардуино
            serial, command_num = Arduino_Serial(script_file_path=script_file_path,
                                                 errs_path=errs_path,
                                                 Arduino_port=Arduino_port)

            # Возвращаем флаг удачного завершения процесса передачи данных
            if serial == "OK":
                print("Передача данных окончена")

            # Ожидаем окончания процесса записи видео
            Video_chek.wait()
            # Перепроверяем завершился ли процесс записи видео
            while Video_chek.poll() is None:
                time.sleep(0.5)
            # Выводим код возврата процесса записи видео
            print("Запись видео возвращает:", Video_chek.returncode)
            returncode = Video_chek.returncode
        # Если отсутствует файл прошивки или проект на ПЛИС, ошибка записывается в файл ошибок
        else:
            errors_file.write("Отсутствует файл прошивки или проект на ПЛИС\n")
            errors_ = 1
            # Задаем пустые значения переменных если файла прошивки нет
            sof_file_name = ""
            sof_path = ""
    # Если отсутствует файл сценария, ошибка записывается в файл ошибок
    else:
        errors_file.write("Отправте данные повторно, включая файл сценария\n")
        errors_ = 1
        # Задаем соответствующие значения переменных, если отсутствует файл сценария
        returncode = 1
        script_file_path = ""
        script_file_name = ""
        sof_file_name = ""
        sof_path = ""

    # Закрываем файл ошибок
    errors_file.close()

    # Повторно перепроверяем наличие файла прошивки
    if not (os.path.exists(sof_path)):
        sof_path = "#"
        sof_name = "#"

    # Запускаем функцию копирования файлов отчетности
    #if not (User_path_to_file == ""):
    sof_file_name = sof_file_path.split('/')[-1]
    script_file_name = script_file_path.split('/')[-1]
    print(sof_file_name, script_file_name)
    file_work = File_switch(root_path=root_path,
                            sof_path=sof_path, script_file_path=script_file_path,
                            sof_file_name=sof_file_name,
                            script_file_name=script_file_name,
                            video_return=returncode)

    # Запускаем функциб удаления лишних файлов
    #if User_path_to_file != '':
    chek_delete = Delete_files(root_path=root_path)



    ##  ВАЖНОЕ МЕСТО!!!
    #file_path = '' ## То что получаем от Кирилла
    # Получаем ссылку на скачивание данного архива
    #file_link = File_upload(service=service, folder_id=folder_id, file_path=file_path)
    #print("Ссылка на файл = ", file_link)
    #upload_file = False
    # delete_chek = Old_files_delete(main_folder_id, service)
    # print(delete_chek)
    # upload_file = False
    # except:
    #     print("Неудача при загрузке файлов на Google Drive")
    #     GUI.print_log("Неудача при загрузке файлов на Google Drive")
    # else:
    #     print("Отсутствует файл токена")
    return ("OK", pr_type, command_num, errors_)

# Launch(User_path_to_file="student_zip/grisha.petuxov", root_path="C:/Project_930/Prototype_with_mail_bot_TO_EXE")
