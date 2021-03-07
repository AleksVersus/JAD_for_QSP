import os, json

build_files=[] # это будет список файлов для билда
current_folder=os.getcwd() # получаем абсолютный путь рабочей папки!
tree=os.walk(current_folder) #
for abs_path, folders, files in tree:
	for file in files:
		sp=os.path.splitext(file)
		if sp[1]==".qsps" or sp[1]=='.qsp-txt' or sp[1]=='.txt-qsp':
			build_files.append(abs_path+'\\'+file)
for i in build_files:
	print (i)