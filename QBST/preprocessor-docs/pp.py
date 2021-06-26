import sys, os
import re

# возвращает вхождение регэкспа или пустую строку
def strfind(regex,string):
	instr=re.search(regex,string)
	if instr==None:
		return ""
	else:
		return instr.group(0)

# функция, извлекающая директиву в скобках
def getDirect(string,direct):
	result=string.replace(direct,'',1).strip()[1:-1]
	return result

# функция, добавляющая метку и значение
def addVariable(vares,direct):
	# vares - ссылка на словарь
	if "=" in direct:
		# делим по знаку равенства
		direct_list=direct.split("=")
		vares[direct_list[0]]=direct_list[1]
		vares[direct_list[1]]=direct_list[1]
	else:
		vares[direct]=True

# функция, которая проверяет, выполняется ли условие
def metCondition(vares,direct):
	result=dict()
	# следующий цикл формирует условие с действительными значениями вместо элементов
	for var in vares:
		if var in direct:
			if type(vares[var])==str:
				direct=direct.replace(var,f"'{vares[var]}'")
			else:
				direct=direct.replace(var,f"{vares[var]}")
	direct=direct.replace("''","'")
	direct=direct.replace('""','"')
	direct="out=(True if "+direct+" else False)"
	exec(direct,result)
	return result['out']

# функция, которая правильно открывает блок условия
def openCondition(command,condition,args):
	i_list=re.split(r'\s+',command.strip())
	prev_args=args['if']
	for i in i_list:
		if i=="exclude" and condition==True:
			prev_args["include"]=args["include"]
			args["include"]=False
		if i=="exclude" and condition==False:
			prev_args["include"]=args["include"]
			args["include"]=True
		elif i=="include" and condition==True:
			prev_args["include"]=args["include"]
			args["include"]=True
		elif i=="include" and condition==False:
			prev_args["include"]=args["include"]
			args["include"]=False
		elif i=="nopp" and condition==True:
			prev_args["pp"]=args["pp"]
			args["pp"]=False
		elif i=="nopp" and condition==False:
			prev_args["pp"]=args["pp"]
			args["pp"]=True
		elif i=="savecomm" and condition==True:
			prev_args["savecomm"]=args["savecomm"]
			args["savecomm"]=True
		elif i=="savecomm" and condition==False:
			prev_args["savecomm"]=args["savecomm"]
			args["savecomm"]=False
	args["openif"]=True

# функция, которая правильно закрывает условие
def closeCondition(args):
	prev_args=args["if"]
	args["include"]=prev_args["include"]
	args["pp"]=prev_args["pp"]
	args["savecomm"]=prev_args["savecomm"]

# функция переназначающая локальные для текущего файла режимы из глобальных
def replaceArgs(arguments,args):
	if "include" in args:
		arguments["include"]=args["include"]
	if "pp" in args:
		arguments["pp"]=args["pp"]
	if "savecomm" in args:
		arguments["savecomm"]=args["savecomm"]

# обработка строки. Поиск спецкомментариев
def ppString(text_lines,string,args):
	result=""
	if result!="":
		text_lines.append(result)

# основная функция
def ppThisFile(file_path,args):
	# эта функция будет обрабатывать файл
	# и возвращать результат после препроцессинга
	result_text=[] # результат обработки: список строк
	variables={} # список (словарь) переменных и их значений
	arguments={
		"include":True, # пока включен этот режим, строки добавляются в результат
		"pp":True, # пока включен этот режим, строки обрабатываются парсером
		"openif":False, # отметка о том, что открыт блок условия
		"savecomm":False, # отметка о том, что не нужно удалять специальные комментарии
		"if":{"include":True, "pp":True, "savecomm":False} # список инструкций до выполнения блока условий
	} # словарь режимов
	replaceArgs(arguments,args) # если переданы какие-то глобальные аргументы, подменяем текущие на глобальные
	with open(file_path,'r',encoding='utf-8') as pp_file:
		file_lines=pp_file.readlines() # получаем список всех строк файла
		# перебираем строки в файле
		for line in file_lines:
			command=re.match(r'^!@pp:',line) # проверяем является ли строка командой
			if command==None:
				# если это не команда, обрабатываем строку
				ppString(result_text,line,arguments)
			else:
				# если это команда, распарсим её
				comm_list=re.split(r':',line)
				if arguments["pp"]:
					# только при включенном препроцессоре выполняются все команды
					# проверяем, что за команда
					if strfind(r'^on\n$',comm_list[1])!="":
						# на данном этапе данная команда уже не актуальна
						ppString(result_text,line,arguments)
					elif strfind(r'^off\n$',comm_list[1])!="":
						# на данном этапе данная команда уже не актуальна
						ppString(result_text,line,arguments)
					elif strfind(r'^savecomm\n$',comm_list[1])!="":
						# данная команда включает режим сохранения спецкомментариев
						arguments["savecomm"]=True
					elif strfind(r'^nosavecomm\n$',comm_list[1])!="":
						# данная команда выключает режим сохранения спецкомментариев
						arguments["savecomm"]=False
					elif strfind(r'^endif\n$',comm_list[1])!="":
						# закрываем условие
						closeCondition(arguments)
					elif strfind(r'^var\(.*?\)',comm_list[1])!="":
						# если мы имеем дело с присвоением значения переменной
						direct=getDirect(comm_list[1],'var') # получаем содержимое скобок
						addVariable(variables,direct) # добавляем метку в словарь
					elif strfind(r'^if\(.*?\)',comm_list[1])!="":
						# если мы имеем дело с проверкой условия
						direct=getDirect(comm_list[1],'if') # получаем содержимое скобок
						condition=metCondition(variables,direct) # проверяем условие
						openCondition(comm_list[2],condition,arguments)
				else:
					# при отключенном препроцессоре выполняется только команда endif
					if strfind(r'^endif\n$',comm_list[1])!="":
						# закрываем условие
						closeCondition(arguments)				
		if arguments["openif"]==True:
			closeCondition(arguments)
		print(result_text)
					
					
args={"include":True, "pp":True, "savecomm":False} # глобальные значения
file="test.qsps"
ppThisFile(file,args)