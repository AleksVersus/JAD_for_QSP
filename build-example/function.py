import os

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
				error_file.write("genFilesPaths: File don't exist. Prove path '"+file_path+"'.\n")
	return files_paths

# из списка файлов .qsps .qsp-txt и .txt-qsp создаём файл .qsp по указанному пути
def constructFile(build_list,new_file):
	# получив список файлов из которых мы собираем выходной файл, делаем следующее
	text=""
	for path in build_list:
		with open(path,"r",encoding="utf-8") as file:
			# открываем путь как файл
			text+=file.read()+"\n\r"
	# необходимо записывать файл в кодировке cp1251, txt2gam версии 0.1.1 понимает лишь её
	with open(new_file,"w",encoding="cp1251") as file:
		file.write(text)

# данная функция находит папку проекта или возвращает None
def searchProject(path):
	error=path # запоминаем путь для возможных ошибок
	error_log=[] # список ошибок
	# если путь является файлом, получаем только путь
	if os.path.isfile(path)==True:
		path=os.path.split(path)[0]
	# пока не найден файл проекта
	while os.path.isfile(path+"\\project.json")==False:
		if os.path.ismount(path)==True:
			error_log.append("function.searchProject: not found 'project.json' file for this project. Prove path '"+error+"'.\n")
			break
		path=os.path.split(path)[0]
	else:
		return path
	if len(error_log)>0:
		with open("errors.log","a",encoding="utf-8") as error_file:
			for i in error_log:
				error_file.write(i)

def exitFiles(work_dir,game_name):
	exit_qsp=work_dir+"\\"+game_name
	exit_txt=work_dir+"\\"+os.path.splitext(game_name)[0]+".txt"
	return [exit_txt,exit_qsp]