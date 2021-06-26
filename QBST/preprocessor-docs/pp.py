import sys, os
import re

def strfind(regex,string):
	instr=re.search(regex,string) # получаем вхождения
	if instr==None:
		return ""
	else:
		return instr.group(0)

def ppString(string):
	pass

def getDirect(string,direct):
	result=string.replace(direct,'',1).strip()[1:-1]
	return result

def addVariable(vares,direct):
	# variables - ссылка на словарь
	if "=" in direct:
		# делим по знаку равенства
		direct_list=direct.split("=")
		vares[direct_list[0]]=direct_list[1]
	else:
		vares[direct]=True

def ppThisFile(file_path):
	# эта функция будет обрабатывать файл
	# и возвращать результат после препроцессинга
	result_text="" # результат обработки
	variables=dict() # список (словарь) переменных и их значений
	arguments={"include":True,"process":True,"openif":False} # словарь
	with open(file_path,'r',encoding='utf-8') as pp_file:
		file_lines=pp_file.readlines() # получаем список всех строк файла
		# перебираем строки в файле
		for line in file_lines:
			command=re.match(r'^!@pp:',line) # проверяем является ли строка командой
			if command==None:
				# если это не команда, обрабатываем строку
				result_text=ppString(line)
			else:
				# если это команда, распарсим её
				comm_list=re.split(r':',line)
				# проверяем, что за команда
				if strfind(r'^on\n$',comm_list[1])!="":
					print('on') # ничего не делаем
				elif strfind(r'^off\n$',comm_list[1])!="":
					print('off') # ничего не делаем
				elif strfind(r'^var\(.*?\)',comm_list[1])!="":
					# если мы имеем дело с присвоением значения переменной
					direct=getDirect(comm_list[1],'var')
					addVariable(variables,direct)
				elif strfind(r'^if\(.*?\)',comm_list[1])!="":
					# если мы имеем дело с проверкой условия
					pass

	print(variables)
					
					

file="test.qsps"
ppThisFile(file)