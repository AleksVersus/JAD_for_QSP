import sys, os
import pp

# данная функция составляет список файлов .qsps .qsp-txt .txt-qsp в указанной папке и вложенных папках
def getFilesList(folder):
	error=folder # запоминаем путь для возможных ошибок
	build_files=[] # это будет список файлов для билда
	tree=os.walk(folder) # получаем все вложенные файлы и папки в виде объекта-генератора
	for abs_path, folders, files in tree:
		# перебираем файлы и выбираем только нужные нам
		for file in files:
			sp=os.path.splitext(file) # получаем путь к файлу в виде ГОЛОВА.ХВОСТ, где ХВОСТ - расширение
			if sp[1]==".qsps" or sp[1]=='.qsp-txt' or sp[1]=='.txt-qsp':
				# если это наше расширение
				# добавляем файл в список к билду
				build_files.append(abs_path+'\\'+file)
	if len(build_files)==0:
		with open("errors.log","a",encoding="utf-8") as error_file:
				error_file.write("function.getFilesList: Folder is empty. Prove path '"+error+"'.\n")
	return build_files

# функция преобразует список словарей, содержащих пути, в список путей
def genFilesPaths(files):
	files_paths=[]
	for path in files:
		# перебираем указанные файлы (каждый элемент списка представляет собой словарь)
		file_path=os.path.abspath(path["path"]) # приводим путь к абсолютному
		if os.path.isfile(file_path):
			files_paths.append(file_path) # если файл существует
		else:
			with open("errors.log","a",encoding="utf-8") as error_file:
				error_file.write("function.genFilesPaths: File don't exist. Prove path '"+file_path+"'.\n")
	return files_paths

# из списка файлов .qsps .qsp-txt и .txt-qsp создаём файл .txt в фформате TXT2GAM по указанному пути
def constructFile(build_list,new_file,pponoff,pp_markers):
	# получив список файлов, из которых мы собираем выходной файл, делаем следующее
	text="" # выходной текст
	print(pponoff,new_file)
	for path in build_list:
		# открываем путь как файл
		with open(path,"r",encoding="utf-8") as file:
			if pponoff=="Hard-off":
				text_file=file.read()+"\r\n" # файл не отправляется на препроцессинг
			elif pponoff=="Off":
				first_string=file.readline()[:]
				second_string=file.readline()[:]
				file.seek(0)
				if first_string=="!@pp:on\n" or second_string=="!@pp:on\n":
					arguments={"include":True, "pp":True, "savecomm":False}
					# файл отправляется на препроцессинг
					text_file=pp.ppThisFile(path,arguments,pp_markers)+'\r\n'
				else:
					text_file=file.read()+"\r\n"
			elif pponoff=="On":
				first_string=file.readline()[:]
				second_string=file.readline()[:]
				file.seek(0)
				if first_string=="!@pp:off\n" or second_string=="!@pp:off\n":
					text_file=file.read()+"\r\n"
				else:
					arguments={"include":True, "pp":True, "savecomm":False}
					text_file=pp.ppThisFile(path,arguments,pp_markers)+'\r\n'
			text+=text_file
	# если папка не создана, нужно её создать
	path_folder=os.path.split(new_file)[0]
	if os.path.exists(path_folder)!=True:
		os.makedirs(path_folder)
	# необходимо записывать файл в кодировке utf-16le, txt2gam версии 0.1.1 понимает её
	text=text.encode('utf-16-le', 'ignore').decode('utf-16-le','ignore')
	with open(new_file,"w",encoding="utf-16-le") as file:
		file.write(text)

# данная функция находит папку проекта или возвращает None
def searchProject(path):
	error=path # запоминаем путь для возможных ошибок
	# если путь является файлом, получаем только путь
	if os.path.isfile(path)==True:
		path=os.path.split(path)[0]
	# пока не найден файл проекта
	while os.path.isfile(path+"\\project.json")==False:
		if os.path.ismount(path)==True:
			with open("errors.log","a",encoding="utf-8") as error_file:
				error_file.write("function.searchProject: not found 'project.json' file for this project. Prove path '"+error+"'.\n")
			break
		path=os.path.split(path)[0]
	else:
		return path

# функция возвращает словарь команд, в зависимости от полученных от системы аргументов
def parseARGS(arguments):
	args={}
	for a in arguments:
		if a=="--buildandrun" or a=="--br" or a=="--b" or a=="--build":
			args["build"]=True
		if a=="--buildandrun" or a=="--br" or a=="--r" or a=="--run":
			args["run"]=True
		if os.path.isfile(a):
			args["point_file"]=os.path.abspath(a)
	if (not "build" in args) and (not "run" in args):
		args["build"]=True
		args["run"]=True
	if not "build" in args:
		args["build"]=False
	if not "run" in args:
		args["run"]=False
	if not "point_file" in args:
		args["point_file"]=os.getcwd()+"\\"+sys.argv[0]
	return args


# из переданного названия файла получаем пути к промежуточному файлу и конечному
def exitFiles(game_path):
	exit_qsp=os.path.abspath(game_path)
	exit_txt=os.path.abspath(os.path.splitext(game_path)[0]+".txt")
	return [exit_qsp,exit_txt]

# распечатка на экране списка
def printList(cur_list):
	for i in cur_list:
		print(i)
	print (":)")