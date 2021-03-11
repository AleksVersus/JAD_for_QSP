# QSP-builder предназначен для сборки отдельных игр формата .qsp
# из текстовых файлов, написанных в формате TXT2GAM

import os, json, subprocess #импортируем нужные модули
import function as qsp # импортируем свой модуль с коротким именем qsp

# заранее определяем пути к плееру и утилите TXT2GAM
txt2gam="D:\\my\\GameDev\\QuestSoftPlayer\\QSP 570 QG 400b\\txt2gam.exe" # путь к txt2gam
player_exe="D:\\my\\GameDev\\QuestSoftPlayer\\QSP 570 QG 400b\\qspgui.exe"

# получать имя файла (или полный путь к нему) мы будем из аргументов к скрипту, пока задаём вручную
point_file = "D:\\my\\GameDev\\QuestSoftPlayer\\projects\\JAD\\build-example\\обязательные локации\\[death]\\death.qsps"

# теперь нам нужно найти файл проекта, это делаем с помощью searchProject
# и выполняем весь остальной код только при наличии файла проекта
work_dir = qsp.searchProject(point_file)
if work_dir!=None:
	# итак, если у нас есть рабочая дирректория, выставляем её, как текущую рабочу папку для удобства
	os.chdir(work_dir)
	# открываем файл project.json через обёртку with и получаем структуру json-файла
	with open("project.json","r",encoding="utf-8") as project_file:
		root=json.load(project_file)

	# инициализируем разные данные
	
	# получаем список инструкций из элемента "project"
	for instruction in root["project"]:
		build_files=[] # этот список будет содержать названия файлов, из которых билдим новый
		# каждая инструкция снова представляет собой словарь
		# однако элементы в этом словаре могут как присутствовать, так и отсутствовать, поэтому
		if "files" in instruction:
			# если инструкция содержит элемент files
			build_files.extend(qsp.genFilesPaths(instruction["files"]))
		if "build" in instruction:
			# если инструкция содержит элемент "build"
			exit_qsp, exit_txt = qsp.exitFiles(work_dir,instruction["build"])
		else:
			pass