# QSP-builder предназначен для сборки отдельных игр формата .qsp
# из текстовых файлов, написанных в формате TXT2GAM

import sys # импортируем системные файлы
import os, json, subprocess #импортируем нужные модули
import function as qsp # импортируем свой модуль с коротким именем qsp

# заранее определяем пути к плееру и утилите TXT2GAM
txt2gam="D:\\my\\GameDev\\QuestSoftPlayer\\QSP 570 QG 400b\\txt2gam.exe" # путь к txt2gam
player_exe="D:\\my\\GameDev\\QuestSoftPlayer\\QSP 570 QG 400b\\qspgui.exe"

# получаем набор команд из аргументов
args=qsp.parseARGS(sys.argv[1:])

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
	export_files=[] # список файлов, получаемых на выходе
	start_file="" # файл, который мы должны запустить
	# получаем список инструкций из элемента "project"
	for instruction in root["project"]:
		build_files=[] # этот список будет содержать названия файлов, из которых билдим новый
		# каждая инструкция снова представляет собой словарь
		# однако элементы в этом словаре могут как присутствовать, так и отсутствовать, поэтому
		if "files" in instruction:
			# если инструкция содержит элемент files
			build_files.extend(qsp.genFilesPaths(instruction["files"]))
		if "folders" in instruction:
			# если инструкция содержит элемент folders
			for path in instruction["folders"]:
				# перебираем все пути, кидаем их функции getFilesList
				build_files.extend(qsp.getFilesList(os.path.abspath(path["path"])))
		if (not "files" in instruction) and (not "folders" in instruction):
			# если не определены инструкции по сборке, собираем из текущей папки
			build_files.extend(qsp.getFilesList(os.getcwd()))
		# if "top_location" in instruction:
			# данная инструкция пока не поддерживается
			# pass
		if "build" in instruction:
			# если инструкция содержит элемент "build"
			exit_qsp, exit_txt = qsp.exitFiles(instruction["build"])
		else:
			# если инструкция не содержит элемент "build"
			num=root["project"].index(instruction) # получаем номер инструкции в списке project
			exit_qsp, exit_txt = qsp.exitFiles("game%i.qsp" %num) # генерируем название файла по номеру инструкции
			with open("errors.log","a",encoding="utf-8") as error_file:
				error_file.write("main: Key 'build' not found in project-list. Choose export name "+exit_qsp+".\n")
		# после того, как все данные получены, генерируем выходной файл
		# собираем текстовый файл
		qsp.constructFile(build_files,exit_txt)
		# теперь нужно конвертировать файл в бинарник
		subprocess.run([txt2gam,exit_txt,exit_qsp])
		if os.path.isfile(exit_qsp):
			export_files.append(exit_qsp)
		# теперь удаляем промежуточный файл
		os.remove(exit_txt)
	# далее нам нужно запустить или не запустить один из файлов в плеере
	if "start" in root:
		# если есть инструкция для запуска файла
		start_file=os.path.abspath(root["start"])
	if (not "start" in root) or (not start_file in export_files):
		start_file=export_files[0]
		with open("errors.log","a",encoding="utf-8") as error_file:
			error_file.write("main: Start-file is wrong. Used '"+start_file+"' for start the player.\n")
	# после обработки json можно запустить указанный файл в плеере
	if not os.path.isfile(start_file):
		with open("errors.log","a",encoding="utf-8") as error_file:
			error_file.write("main: Start-file is wrong. Don't start the player.\n")
	else os.path.isfile(player_exe) and :
		# здесь может быть: иначе если передана команда на запуск!
		subprocess.run([player_exe,start_file])