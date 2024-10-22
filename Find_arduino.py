import sys
import os
import warnings
import time
import serial.tools.list_ports
import subprocess
import configparser

def Find_Arduino(root_path):
    # Раздел статичных переменных

    # Обращение к файлу настроек
    config = configparser.ConfigParser()
    config_path = root_path + '/' + "Config.ini"
    config.read(config_path)

    # Путь до программатора Arduino
    Arduino_path_1 = config['Arduino']['arduino_avrdude_1']

    # Путь до конфигуратора программатора Arduino
    Arduino_path_2 = config['Arduino']['arduino_avrdude_2']

    if os.path.exists(Arduino_path_1):  # Проверяем существует ли данный путь исполняемых файлов
        Arduino_path_1 = Arduino_path_1

    else:
        find_in = "C:/Program Files (x86)/Arduino/hardware/tools/avr"  # Задаем корневую папку
        name = "avrdude.exe"
        for root, dirs, files in os.walk(find_in):  # В цикле проходим все папки и файлы в корневой папке
            if name in files:
                Arduino_path_1 = '' + root + '/' + name  # Добавляем в путь папки и необходимый файл
                config['Arduino']['arduino_avrdude_1'] = Arduino_path_1
                with open('Config.ini', 'w') as configfile:
                    config.write(configfile)
                print(Arduino_path_1)


    if os.path.exists(Arduino_path_2):  # Проверяем существует ли данный путь исполняемых файлов
        Arduino_path_2 = Arduino_path_2

    else:
        find_in = "C:/Program Files (x86)/Arduino/hardware/tools/avr"  # Задаем корневую папку
        name = "avrdude.conf"
        for root, dirs, files in os.walk(find_in):  # В цикле проходим все папки и файлы в корневой папке
            if name in files:
                Arduino_path_2 = '' + root + '/' + name  # Добавляем в путь папки и необходимый файл
                config['Arduino']['arduino_avrdude_2'] = Arduino_path_2
                with open('Config.ini', 'w') as configfile:
                    config.write(configfile)
                print(Arduino_path_2)

    # Путь до hex файла прошивки
    Project_path = config['Direc']['Path']
    # Project_path = "C:/Project_930/Prototype_with_mail_bot"

    Arduino_hex_path = config['Arduino']['arduino_hex_path']

    if os.path.exists(Arduino_hex_path):  # Проверяем существует ли данный путь исполняемых файлов
        Arduino_hex_path = Arduino_hex_path

    else:
        find_in = Project_path  # Задаем корневую папку
        for root, dirs, files in os.walk(find_in):  # В цикле проходим все папки и файлы в корневой папке
            for name in files:
                if name.endswith("ino.hex"):
                    Arduino_hex_path = '' + root + '/' + name  # Добавляем в путь папки и необходимый файл
                    config['Arduino']['arduino_hex_path'] = Arduino_hex_path
                    with open('Config.ini', 'w') as configfile:
                        config.write(configfile)
                    print(Arduino_hex_path)

    # Ключ успешного ответа Serial порта

    start = config['Arduino']['arduino_key']
    # Ключ ошибки
    Error = "Arduino_problem"
    Arduino_name = config['Arduino']['arduino_name']

    int1 = 0
    Arduino_port = ""
    str2 = ""

    # Поиск активных COM портов
    arduino_ports = [
        p.device
        for p in serial.tools.list_ports.comports()
        if Arduino_name in p.description  # Поиск марки Arduino в списке подключенных устройств.
    ]
    # Обработка исключений
    if not arduino_ports:
        raise IOError("Плата Arduino не найдена")
    if len(arduino_ports) > 1:
        warnings.warn('Найдено несколько плат, использоваться будет первая')

    # Поиск подключенной платы Arduino в списке подключенных устройств
    for p in serial.tools.list_ports.comports():
        if Arduino_name in p.description:
            while int1 < 9:  # В цикле проходим порты от "COM0" до "COM8".

                if Arduino_name in p[1]:  # Ищем подходящее название Arduino в p[1].
                    str2 = str(int1)  # Конвертируем номер порта из int в str:
                    Arduino_port = "COM" + str2  # Соединяем номер порта с его названием.

                if Arduino_name in p[1] and Arduino_port in p[
                    1]:  # Ещё раз ищем название платы Arduino и номер COM порта"
                    # print ("Найдена  " + Arduino_name + Arduino_port + "\n")
                    int1 = 9  # Выходим из цикла.

                if int1 == 8:
                    # print ("Плата не найдена")
                    sys.exit()  # Прекращение выполнения скрипта.

                int1 = int1 + 1

    time.sleep(1)  # Выставляем задержку в 1 секунду.

    # Проверка Serial порта

    ok = 0  # Флаг неверной прошивки на Arduino
    neok = 0  # Флаг успешного соединения с Arduino
    ser = serial.Serial(Arduino_port, 9600, timeout=0.1)  # Подключение по Serial порту к Arduino.
    time.sleep(3)
    # Проверка на успешное соединение
    if ok == 0 and ser:
        y = 0
        # print("Попытка подключения к Serial порту")
        while y != 1:  # Выставляем повторение подключений до успешного
            poslanie = "Hello"
            # print("prohodka")
            ser.write(bytes(poslanie, 'utf-8'))  # Отправляем через Serial порт ключевое слово
            data = str(ser.read(size=10))
            time.sleep(0.5)

            if str(data).count(start[0]):  # В случае получения контрольной последовательности
                print("Плата Ардуино готова к работе")

                neok = 1  # Переводим флаг перепрошивки платы в неактивное положение
                Arduino_flash_complete = "no"  # Заполняем итоговую переменную перепрошивки платы
                y += 1

    # Перепрошивка платы необходимой прошивкой
    if neok == 0:
        print("Плата Ардуино перепрошивается\n")

        ser.close()  # Перед перепрошивкой закрываем соединение через Serial порт
        # Перепрошиваем плату Arduino с помощью консольной команды, и выводим ответные сообщения в переменные
        Arduino_flash = subprocess.run('"{0}" -C"{1}" -v -patmega328p -carduino -P{2} -b57600 -D -Uflash:w:"{3}":i'.
                                       format(Arduino_path_1, Arduino_path_2, Arduino_port, Arduino_hex_path),
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        ok = 1  # Переводим флаг перепрошивки платы в активное положение

        # Вывод переменных после перепрошивки платы (использовать в режиме отладки)
        # print(Arduino_flash.stdout, "\n")
        # print(Arduino_flash.stdin, "\n")
        # print(Arduino_flash.stderr, "\n")

        # Получаем результат успешной перепрошивки платы

        # print(Arduino_flash.stderr.split('\n'), "\n")
        # Разбиваем полученное значение по символу переноса строки
        Arduino_flash_complete = Arduino_flash.stderr.split('\n')
        Arduino_flash_complete = str(Arduino_flash_complete[-3])  # Обрезаем возвращаемое значение до одной строки
        print(Arduino_flash_complete, '\n')


        # Ещё раз открываем и закрываем Serial порт, чтобы он точно закрылся после перепрошивки
        ser.close()
        ser.open()
        ser.flushInput()
        ser.flushOutput()
        ser.close()
    # Выполняем проверку на выполнение одного из действий
    if (neok == 1) or ((ok == 1) and (Arduino_flash_complete == "avrdude.exe done.  Thank you.")):
        # print("Соединение с Ардуино успешно\n")
        return (Arduino_port)
    else:
        return (Error)
#print(Find_Arduino())
