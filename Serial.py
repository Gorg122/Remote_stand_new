#Добавлена обработка всех возможных ошибок в тексте текстового файла
#Добавлена проверка на наличие текстового файла
#Добавлена обработка пустых строк
#Добавлено создание папки с названием файла скетча
#Добавлена переменная общего пути


import os
import shutil
import re
import time
import serial

#Actualised a directory with a script.
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

#output_file = open("scetch.ino", "w")
filePath = __file__
main_path = os.getcwd()
users_mail = "example"
file_name = "buttons.txt"
scetch_name = "scetch"
errs_f = "errors.txt"
output_dir = os.path.join(main_path,users_mail)
#erros_path = os.path.join(main_path, )
file_path = os.path.join(main_path, file_name)
errs_path = os.path.join(main_path, errs_f)
errors_file = open(errs_path + "errors.txt", "w")

if os.path.exists(file_path):

    # выведем все строки включая пустые

    print(len(re.findall(r"[\n']+?", open(file_path).read())))
    all_strings = len(re.findall(r"[\n']+?", open(file_path).read()))

    # выведем количество без пустых строк
    print(len(re.findall(r"[\n']+", open(file_path).read())))
    strings = len(re.findall(r"[\n']+", open(file_path).read()))
    # if all_strings != strings:
    #     errors_file.write("Ваш файл сценария не должен содержать пустых строк\n")
    input_file = open(file_path)

    lines = input_file.readlines()
    scetch_dir = os.path.join(main_path, scetch_name)
    if os.path.exists(scetch_dir):
        shutil.rmtree(scetch_dir)
        #os.rmdir(scetch_dir)
    else:
        os.mkdir(scetch_dir)
    scetch_path = os.path.join(scetch_dir, scetch_name)


    but = ["button"]
    sw = ["switch"]
    end = ["end"]
    empty = [""]
    numbers = ["0","9"]
    delay = ["delay"]
    # start = ["start"]
    switches = dict([(1, 0),(2, 0),(3, 0),(4, 0),(5, 0),(6, 0),(7, 0),(8, 0)])

    arduino = serial.Serial(port='COM6', baudrate=9600, timeout=.1) # Инициализируем Serial port

    y = 0
    #waiting for device
    time.sleep(3)
    while y != 1:
        poslanie = "Hellohel\n"
        print("prohodka")
        #st = str(poslanie)
        arduino.write(bytearray(poslanie, 'utf-8'))
        #data = arduino.readline()
        #data = arduino.read(arduino.inWaiting())
        data = str(arduino.readline().decode().strip('\r\n'))
        if str(data).count(start[0]):
            print("Poluchenorazhreshenie")
            #data = ""
            #poslanie = "1H"
            #arduino.write(bytes(poslanie, 'utf-8'))
            y += 1
    data = arduino.read(arduino.inWaiting())
    for i in range(all_strings):

        # if (lines[i] == "\n"):
        #     i = i + 1
        #     print("Empty string")
        #print(lines[i][-2])
        num = re.findall(r'\d+', str(lines[i]))
        false_pin = False
        # #if (i != all_strings):
        #     #if (int(lines[i][-2]) > 8) or (intвудфн(lines[i][-2]) < 1):
        # print(num)
        if (lines[i] != "\n"):
            print(num[0])
            if (int(num[0]) > 8) or (int(num[0]) < 1):
                i += 1
                false_pin = True
                errors_file.write("Количество активных пинов равно 9 (строка " + str(i) + ")\n")
                print("not write pin\n")
        if (lines[i] == "\n"):
             i += 1
             print("Empty string")
        # if (i):
        #     i = i + 1
        #     errors_file.write("Количество активных пинов равно 9\n")
        #     print("Количество активных пинов равно 9\n")

        elif (false_pin == False):
            if (lines[i].count(but[0])): #Кнопки
                curent_pin = num[0]
                comand_but1 = str(curent_pin) + "H\n"
                y = 0
                data = ""
                #while y != 1:
                arduino.write(bytearray(comand_but1, 'utf-8'))
                #arduino.write(bytes("", 'utf-8'))
                time.sleep(1)
                    #if data.count(h1[0]):
                        #y += 1
                print("EST")
                #arduino.write(bytes("Hoy", 'utf-8'))
                print(comand_but1)
                time.sleep(0.1)
                print(data)
                data = ""
                time.sleep(0.1)
                comand_but2 = str(curent_pin) + "L\n"
                arduino.write(bytearray(comand_but2, 'utf-8'))
                print(comand_but2)
                time.sleep(0.1)
                print(data)
                current_commands += 1
                # print("digitalWrite(pin" + str(curent_pin) + ", HIGH);\n delay(100)\n digitalWrite(pin"+str(curent_pin)+", LOW);\n")
                #
                # output_file.write("digitalWrite(pin" + str(curent_pin) + ", HIGH);\n delay(100);\n digitalWrite(pin"+str(curent_pin)+", LOW);\n")
            # elif (lines[i].count(sw[0])):
            #     if switches[i-1] == 0:
            #         print("digitalWrite(pin" + str(lines[i][-2]) + ", HIGH);\n sleep(500)\n")  # digitalWrite(pin"+str(lines[i][-2])+", LOW);\n")
            #         output_file.write("digitalWrite(pin" + str(lines[i][-2]) + ", HIGH);\n sleep(500)\n") #digitalWrite(pin"+str(lines[i][-2])+", LOW);\n")
            #         switches[i-1] = 1

            elif (lines[i].count(sw[0])) and (switches[int(num[0])] == 0) and (false_pin != True): # Свитч 0
                curent_pin = num[0]
                # print("digitalWrite(pin" + str(curent_pin) + ", HIGH);\n delay(100);\n")  # digitalWrite(pin"+str(lines[i][-2])+", LOW);\n")
                # output_file.write("digitalWrite(pin" + str(curent_pin) + ", HIGH);\n delay(100);\n") #digitalWrite(pin"+str(lines[i][-2])+", LOW);\n")
                # switches[int(curent_pin)] = 1
                comand_sw1 = str(curent_pin) + "H\n"
                arduino.write(bytearray(comand_sw1, 'utf-8'))
                print(comand_sw1)
                time.sleep(1)
                print(data)
                time.sleep(0.1)
                switches[int(curent_pin)] = 1
                current_commands += 1

            elif (lines[i].count(sw[0])) and switches[int(num[0])] == 1 and false_pin != True: # Свитч 1
                curent_pin = num[0]
                # print("digitalWrite(pin" + str(curent_pin) + ", LOW);\n delay(100);\n")  # digitalWrite(pin"+str(lines[i][-2])+", LOW);\n")
                # output_file.write("digitalWrite(pin" + str(curent_pin) + ", LOW);\n delay(100);\n") #digitalWrite(pin"+str(lines[i][-2])+", LOW);\n")
                # switches[int(curent_pin)] = 0
                #switches.insert(int(lines[i][-2]),1)
                comand_sw2 = str(curent_pin) + "L\n"
                arduino.write(bytearray(comand_sw2, 'utf-8'))
                print(comand_sw2)
                time.sleep(1)
                print(data)
                time.sleep(0.1)
                switches[int(curent_pin)] = 0
                current_commands += 1

            elif (lines[i].count(end[0])):
                print(switches)
                input_file.close()
                output_file.write("}")
                output_file.close()
                break
else:

    errors_file.write("Файл отсутствует\n")
    print("Файл отсутствует\n")
errors_file.close()