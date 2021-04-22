import sys, os, re, codecs, io

def replBadSym(file_name):
	# заменяем запрещённые символы на символы подчёркивания
	file_name=re.sub(r'<','_',file_name)
	file_name=re.sub(r'>','_',file_name)
	file_name=re.sub(r'\*','_',file_name)
	file_name=re.sub(r'\\','_',file_name)
	file_name=re.sub(r'\/','_',file_name)
	file_name=re.sub(r'\:','_',file_name)
	file_name=re.sub(r'\?','_',file_name)
	file_name=re.sub(r'\|','_',file_name)
	file_name=re.sub(r'\"','_',file_name)
	return file_name

game_adr="game.txt"
proj_adr="game.qproj"
proj_file=[]
folder_path=""
location_dict={} # список/словарь файлов/локаций
location_array={} # словарь, содержащий и названия локаций и их полный текст

if os.path.isfile(game_adr):
	# декодируем файл, убираем BOM
	byte = min(32, os.path.getsize(game_adr))
	raw = open(game_adr,'rb').read(byte)
	encoding='utf-8'
	bt=b''
	if raw.startswith(codecs.BOM_UTF8):
	    encoding='utf-8'
	    bt=codecs.BOM_UTF8
	elif raw.startswith(codecs.BOM_UTF16):
		encoding='utf-16'
		bt=codecs.BOM_UTF16
	if bt!=b'':
		with open(game_adr,'r',encoding=encoding) as file:
			text_game=file.read()
		with open(game_adr,'w',encoding='utf-8') as file:
			file.write(text_game)
	else:
		with open(game_adr,'r',encoding=encoding) as file:
			file.seek(0)
			text_game=file.read()
		with open(game_adr,'w',encoding='utf-8') as file:
			file.write(text_game)

	# данная часть получает словарь типа: имя_локации:размещение в папках
	with open(proj_adr,"r",encoding='utf-8') as proj_file:
		proj_list=proj_file.readlines()
		for i in proj_list:
			location=re.match(r'\s*?<Location name=".*?"/>', i)
			folder=re.match(r'\s*?<Folder name=".*?">', i)
			close_folder=re.match(r'\s.*?</Folder>',i)
			if location!=None:
				name=re.search(r'name=".*?"', i).group(0)
				name=name[6:len(name)-1] # имя локации
				file_name=replBadSym(name)
				if folder_path=="":
					location_dict[name]=file_name+".qsps"
				else:
					location_dict[name]=folder_path+"\\"+file_name+".qsps"
			if folder!=None:
				name=re.search(r'name=".*?"', i).group(0)
				name=name[6:len(name)-1]
				folder_path=replBadSym(name)
			if close_folder!=None:
				folder_path=""
		#for i in location_dict:
		#	print(location_dict[i]) # тест полученных имён локаций.

	# эта часть дробит большой файл на фрагменты, каждый фрагмент помещая в словарь типа название_локации:содержимое
	with open(game_adr,"r",encoding="utf-8") as game_file:
		game_list=game_file.readlines()
		location_name=""
		for i in game_list:
			location_open=re.match(r'#\s*?.+?$',i)
			location_close=re.match(r'---\s*?.+?$',i)
			if location_open!=None:
				# мы нашли начало локации, получаем её имя
				location_name=location_open.group(0)
				location_name=re.sub(r'^#\s*','',location_name)
				location_array[location_name]=i
			elif location_close!=None:
				# мы нашли конец локации, правда ли это конец
				location_array[location_name]+=i 
				ln=location_close.group(0)
				ln=re.sub(r'^---\s+','',ln)
				ln=re.sub(r'\s-+$','',ln)
				if ln==location_name:
					location_name=""
			elif location_name!="":
				location_array[location_name]+=i

	# после того, как были составлены словарь путей и словарь локаций сохраняем файлы
	count=1
	if not os.path.isdir("export_game"):
		os.mkdir("export_game")
	for location_name in location_array:
		if location_name in location_dict:
			# если в списке путей есть указанная локация, берём путь оттуда
			path=location_dict[location_name]
		else:
			# в противном случае сохраняем локацию в текущей папке
			path=location_name+".qsps"
		folder=os.path.split(path)[0]
		if not os.path.isdir("export_game\\"+folder):
			# если дирректория не существует, создаём
			os.mkdir("export_game\\"+folder)
		if os.path.isfile("export_game\\"+path):
			path+="_%i" %count
		with open("export_game\\"+path,"w",encoding="utf-8") as file:
			# теперь сохраняем файлы
			file.write(location_array[location_name])
	# удаляем исходный файл
	os.remove(game_adr)
else:
	print('Error. File "game.txt" is not found!')