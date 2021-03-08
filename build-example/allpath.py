import os

def getFilesList(folder):
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
	return build_files

def constructFile(build_list,new_file):
	# получив список файлов из которых мы собираем выходной файл, делаем следующее
	text=""
	for path in build_list:
		with open(path,"r",encoding="utf-8") as file:
			# открываем путь как файл
			text+=file.read()+"\n\r"
	with open(new_file,"w",encoding="utf-8") as file:
		file.write(text)