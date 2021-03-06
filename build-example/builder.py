import os, json #импортируем нужные модули

# открываем файл через обёртку with
with open("project.json","r",encoding="utf-8") as project_file:
    root=json.load(project_file) # получаем структуру json-файла
    # root["project"] — список инструкций. Перебираем список инструкций:
    for instruction in root["project"]:
        # каждая инструкция представляет собой словарь типа
        # "build": {словарь} или "start":"startgame.qsp"
        # получаем инструкцию:
        this_instruction=list(instruction.keys())[0]
        if this_instruction=="build":
            # если инструкция должна собирать файлы
            # значит она представляет собой словарь
            build=instruction["build"]
            # Получаем список ключей
            build_list=list(build)
            # проверяем, существует ли ключ "folders"
            if "folders" in build_list:
                # если ключ существует, значит мы снова имеем дело со списком:
                print (build["folders"])
