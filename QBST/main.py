# QSP-builder предназначен для сборки отдельных игр формата .qsp
# из текстовых файлов, написанных в формате TXT2GAM

import os, sys # импортируем системные файлы
import json, subprocess #импортируем нужные модули
import re # модуль работы с регулярками
import function as qsp # импортируем свой модуль с коротким именем qsp
import pp # импортируем модуль препроцессора

# заранее определяем пути к плееру и утилите TXT2GAM
txt2gam="D:\\my\\GameDev\\QuestSoftPlayer\\QSP 570 QG 400b\\txt2gam.exe" # путь к txt2gam
player_exe="D:\\my\\GameDev\\QuestSoftPlayer\\QSP 570 QG 400b\\qspgui.exe"

# получаем набор команд из аргументов. Всегда три команды!!!
args=qsp.parseARGS(sys.argv[1:])
# -----------------------------------------------------------------------
# args["point_file"] - отправная точка для поиска project.json
# args["build"] - указание собирать ли проект
# args["run"] - указание запускать ли проект
# -----------------------------------------------------------------------

# теперь нам нужно найти файл проекта, это делаем с помощью searchProject
# и выполняем весь остальной код только при наличии файла проекта
work_dir = qsp.searchProject(args["point_file"])
if work_dir!=None:
	# итак, если у нас есть рабочая дирректория, выставляем её, как текущую рабочу папку для удобства
	os.chdir(work_dir)
	# открываем файл project.json через обёртку with и получаем структуру json-файла
	with open("project.json","r",encoding="utf-8") as project_file:
		root=json.load(project_file)
	# получаем пути к txt2gam и плееру
	if "converter" in root:
		if os.path.isfile(os.path.abspath(root["converter"])):
			txt2gam=os.path.abspath(root["converter"])
	if "player" in root:
		if os.path.isfile(os.path.abspath(root["player"])):
			player_exe=os.path.abspath(root["player"])
	if "save_txt2gam" in root:
		if root["save_txt2gam"]=="True":
			save_txt2gam=True
		else:
			save_txt2gam=False
	else:
		save_txt2gam=False
	# инициализируем разные данные
	export_files=[] # список файлов, получаемых на выходе
	start_file="" # файл, который мы должны запустить
	if args["build"]==True and args["run"]==True:
		print("Build and Run Mode")
	elif args["build"]==True:
		print("Build Mode")
	elif args["run"]==True:
		print("Run Mode")
	if args["build"]==True:
		pp_markers={"Initial":True,"True":True,"False":False} # словарь глобальных меток для препроцессора
		if not "preprocessor" in root:
			root["preprocessor"]="Off"
		# только если разрешена сборка файла
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
			qsp.constructFile(build_files,exit_txt,root["preprocessor"],pp_markers)
			# теперь нужно конвертировать файл в бинарник
			subprocess.run([txt2gam,exit_txt,exit_qsp],stdout=subprocess.PIPE)
			if os.path.isfile(exit_qsp):
				export_files.append(exit_qsp)
			# теперь удаляем промежуточный файл
			if save_txt2gam==False:
				os.remove(exit_txt)

	if args["run"]==True:
		# если разрешён запуск
		if "start" in root:
			# если есть инструкция для запуска файла
			start_file=os.path.abspath(root["start"])
		if ((not "start" in root) or (not os.path.isfile(start_file))) and len(export_files)>0:
			# если нет инструкции или указанный файл не существует, но есть список файлов
			start_file=export_files[0]
			with open("errors.log","a",encoding="utf-8") as error_file:
				error_file.write("main: Start-file is wrong. Used '"+start_file+"' for start the player.\n")
			# если нет ни инструкции, ни списка файлов start_file будет иметь пустое значение
		if ((not "start" in root) or (not os.path.isfile(start_file))) and os.path.splitext(args["point_file"])[1]==".qsp":
			start_file=args["point_file"]
		# после обработки json можно запустить указанный файл в плеере
		if not os.path.isfile(player_exe):
			with open("errors.log","a",encoding="utf-8") as error_file:
				error_file.write("main: Path at player is wrong. Prove path '"+player_exe+"'.\n")
		if not os.path.isfile(start_file):
			# если указан неправильный файл запуска
			with open("errors.log","a",encoding="utf-8") as error_file:
				error_file.write("main: Start-file is wrong. Don't start the player.\n")
		else:
			proc=subprocess.Popen([player_exe,start_file])
			# эта инструкция завершает скрипт через 100 мс уже после вызова плеера
			# это нужно, чтобы окно консоли не подвисало, когда уже запущен плеер,
			# но и плеер должен открыться выше окна консоли.
			try:
				proc.wait(0.1)
			except subprocess.TimeoutExpired:
				pass