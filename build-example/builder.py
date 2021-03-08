import os, json, subprocess #импортируем нужные модули
import allpath # импортируем свой модуль

error_log=[] # список ошибок
work_dir=os.getcwd() # текущая рабочая папка относительно файла project.json
txt2gam="D:\\my\\GameDev\\QuestSoftPlayer\\QSP 570 QG 400b\\txt2gam.exe" # путь к txt2gam
player_exe="D:\\my\\GameDev\\QuestSoftPlayer\\QSP 570 QG 400b\\qspgui.exe"
exit_files_list=[] # список выходных файлов
# открываем файл json через обёртку with
with open("project.json","r",encoding="utf-8") as project_file:
    root=json.load(project_file) # получаем структуру json-файла
    # root["project"] — список инструкций. Перебираем список инструкций:
    for instruction in root["project"]:
        # каждая инструкция представляет собой словарь типа
        # "build": {словарь} или "start":"startgame.qsp"
        # получаем инструкцию:
        this_instruction=list(instruction.keys())[0]
        if this_instruction=="build":
            build_files=[] # список файлов для билда
            game_name="game.qsp" # название игры по умолчанию
            # если инструкция должна собирать файлы
            # значит она представляет собой словарь
            build=instruction["build"]
            # проверяем, существует ли ключ "folders"
            if "folders" in build:
                path_list=[]
                # если ключ существует, значит мы снова имеем дело со списком:
                for path in build["folders"]:
                    # перебираем все пути, кидаем их функции getFilesList
                    build_files.extend(allpath.getFilesList(os.path.abspath(path["path"])))
                    path_list.append(path["path"])
            # на этом этапе в build_files размещены точные пути ко всем build файлам
            if "export" in build:
                # если ключ существует, меняем имя на указанное
                game_name=build["export"]
            if len(build_files)==0:
            # если нечего собирать, добавляем информацию в лог
                log=""
                for path in path_list:
                    log+=path
                error_log.append("Build List is empty: "+log)
                del log
            else:
            # если есть чего собирать, собираем:
                # путь к выходному файлу ставится относительно рабочей папки
                exit_txt=work_dir+"\\"+os.path.splitext(game_name)[0]+".txt"
                # путь к конечному файлу
                exit_qsp=work_dir+"\\"+game_name
                # собираем текстовый файл
                allpath.constructFile(build_files,exit_txt)
                # теперь нужно конвертировать файл в бинарник
                subprocess.run([txt2gam,exit_txt,exit_qsp])
                if os.path.isfile(exit_qsp):
                    exit_files_list.append(exit_qsp)
                # теперь удаляем промежуточный файл
                os.remove(exit_txt)
            del path_list
        if this_instruction=="start":
            start_file=work_dir+"\\"+instruction["start"]
            if not start_file in exit_files_list:
                start_file=exit_files_list[0]
            print (start_file)
# после обработки json можно запустить указанный файл в плеере
