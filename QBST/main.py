# QSP-builder

# Sorry My BAD English!!!

# Build the game-files in ".qsp"-format from text-files in TXT2GAM-format.
# Собирает файлы игр формата ".qsp" из текстовых файлов формата TXT2GAM.

# Don't use this script as module! Не используйте этот скрипт, как модуль!

# Importing standart modules.
import sys
import os 
import subprocess
import json
import re

# Importing my modules.
import function as qsp
import pp

# Default paths to converter and player.
txt2gam="C:\\Program Files\\QSP\\converter\\txt2gam.exe"
player_exe="C:\\Program Files\\QSP\\qsp570\\qspgui.exe"

# Three commands from arguments.
args=qsp.parse_args(sys.argv[1:])

# -----------------------------------------------------------------------
# args["point_file"] - start point for search `project.json`
# args["build"] - command for build the project
# args["run"] - command for run the project
# -----------------------------------------------------------------------

# Search the project-file. Ищем файл проекта.
work_dir = qsp.search_project(args["point_file"])

if qsp.need_project_file(work_dir, args["point_file"], txt2gam, player_exe):
	# If project-file is not found, but other conditional is right, generate the new project-file.
	game_name = os.path.splitext(os.path.split(args["point_file"])[1])[0]
	work_dir = os.path.abspath('.')
	project_json = qsp.get_standart_project(game_name, args["point_file"], txt2gam, player_exe)
	project_json = project_json.replace('\\', '\\\\')
	with open(work_dir+"\\project.json","w",encoding="utf-8") as file:
		file.write(project_json)
	with open("errors.log","a",encoding="utf-8") as error_file:
		error_file.write(f"File '{work_dir}\\project.json' was created.\n")

if work_dir is not None:
	# Change work dir:
	os.chdir(work_dir)

	# Deserializing project-file:
	with open("project.json","r",encoding="utf-8") as project_file:
		root=json.load(project_file)

	# Get paths to converter and player (not Deafault)
	if "converter" in root:
		if os.path.isfile(os.path.abspath(root["converter"])):
			txt2gam=os.path.abspath(root["converter"])
	if "player" in root:
		if os.path.isfile(os.path.abspath(root["player"])):
			player_exe=os.path.abspath(root["player"])

	# Save temp-files Mode:
	if "save_txt2gam" in root:
		if root["save_txt2gam"]=="True":
			save_txt2gam=True
		else:
			save_txt2gam=False
	else:
		save_txt2gam=False

	# Postprocessor's scripts list (or none):
	if "postprocessors" in root:
		include_scripts=root["postprocessors"]
	else:
		include_scripts=None

	# Generate location with files-list.	
	if ("scans" in root) and ("start" in root):
		if "location" in root["scans"]:
			prove_file_loc=root["scans"]["location"]
		else:
			prove_file_loc="prvFile"
		found_files=[] # Absolute files paths
		start_file=os.path.abspath(root["start"])
		start_file_folder=os.path.split(start_file)[0]
		if "folders" in root["scans"]:
			scans_folders=root["scans"]["folders"] # folders for scans
			for folder in scans_folders:
				# Iterate through the folders, comparing the paths with start_file,
				# to understand if the folder lies deeper relative to it.
				sf,f=qsp.compare_paths(start_file_folder,os.path.abspath(folder))
				if sf=='':
					# Folder relative to path.
					found_files.extend(qsp.getFilesList(folder,filters=[]))
				else:
					# Folder is not relative to path. Is error.
					with open("errors.log","a",encoding="utf-8") as error_file:
						error_file.write(f"Folder '{folder}' is not in the project.\n")
		if "files" in root["scans"]:
			scans_files=root["scans"]["files"]
			for file in scans_files:
				sf,f=qsp.compare_paths(start_file_folder,os.path.abspath(file))
				if sf=='':
					# если папка находится относительно данного пути
					found_files.append(os.path.abspath(file))
				else:
					# если папка не находится относительно данного пути, нужно сделать запись об ошибке
					with open("errors.log","a",encoding="utf-8") as error_file:
						error_file.write(f"File '{file}' is not in the project.\n")
		qsp_file_body=[
			'QSP-Game Функция для проверки наличия файлов\n',
			f'# {prove_file_loc}\n',
			'$args[0]=$args[0] & !@ путь к файлу, который нужно проверить\n',
			'$args[1]="\n'
		]
		for file in found_files:
			sf,f=qsp.compare_paths(start_file_folder,os.path.abspath(file))
			qsp_file_body.append(f'[{f}]\n')
		qsp_file_body.extend([
			'"\n',
			'if instr($args[1],"[<<$args[0]>>]")<>0: result=1 else result=0\n',
			f'--- {prove_file_loc} ---\n'
		])
		# Create file next to project-file:
		with open('.\\prvFile_location.qspst', 'w',encoding='utf-8') as file:
			file.writelines(qsp_file_body)
		# Add file-path to build:
		if "files" in root["project"][0]:
			root["project"][0]["files"].append({"path":".\\prvFile_location.qspst"})
		else:
			root["project"][0]["files"]=[{"path":".\\prvFile_location.qspst"}]

	# Data init.
	export_files=[]
	start_file="" # File, that start in player.
	print_builder_mode(args["build"], args["run"])
	if args["build"]==True:
		pp_markers={"Initial":True,"True":True,"False":False} # Preproc markers.
		if not "preprocessor" in root:
			root["preprocessor"]="Off"
		# Get instructions list from "project".
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
			if "postprocessor" in instruction:
				# если указаны скрипты постпроцессора, назначаем их
				# таким образом, не важно, выставили мы общие скрипты, или нет
				# если их прописать отдельно, они выполнятся для отдельного билда
				include_scripts=instruction["postprocessors"]
			# после того, как все данные получены, генерируем выходной файл
			# собираем текстовый файл
			qsp.constructFile(build_files,exit_txt,root["preprocessor"],pp_markers)
			# перед конвертированием можно прогнать каждый файл скриптами постпроцессора
			if include_scripts!=None:
				for script in include_scripts:
					subprocess.run([sys.executable,script,exit_txt],stdout=subprocess.PIPE)
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