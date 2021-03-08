import os, json #импортируем нужные модули
import allpath # импортируем свой модуль

error_log=[] # список ошибок
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
                pass
            del path_list
            