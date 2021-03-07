import os, json

build_list=[] # создаём список файлов, из которых потом будем билдить общий txt2gam
# получаем список файлов в текущей папке
all_files=os.listdir(".") # точка в данном случае вполне работает, как указатель на текущую папку
# перебираем все пути в списке
while len(all_files)>0:
	print(all_files[0]),
	if os.path.isdir(all_files[0])==True:
		print ("this folder")
		# если путь является папкой:
		targfold_files=os.listdir(all_files[0]) # получаем список файлов в указанной папке
		all_files.extend(targfold_files) # добавляем полученный список к исходному
		del targfold_files
	else:
		sp=os.path.splitext(all_files[0])
		# если путь является файлом
		if (sp[1]==".qsps") or (sp[1]==".qsp-txt") or (sp[1]==".txt-qsp"):
			print (all_files[0], "< add in build_list")
			build_list.append(all_files[0])
			break
	del all_files[0]
print (all_files)
print (build_list)