import re

# возвращает вхождение регэкспа или пустую строку
def strfind(regex, string):
	instr = re.search(regex, string)
	if instr == None:
		return ""
	else:
		return instr.group(0)

# функция, извлекающая директиву в скобках
def get_direct(string, direct):
	result = string.replace(direct, '', 1).strip()[1:-1]
	return result

# функция, добавляющая метку и значение
def add_variable(vares, direct):
	temp = [False, False]
	# vares - ссылка на словарь
	if "=" in direct:
		# делим по знаку равенства
		direct_list = direct.split("=")
		temp[0] = vares[direct_list[0]] if direct_list[0] in vares else direct_list[0]
		temp[1] = vares[direct_list[1]] if direct_list[1] in vares else direct_list[1]
		if direct_list[0] in vares and type(vares[direct_list[0]]) == bool:
			...
		else:
			vares[direct_list[0]] = temp[1]
		if direct_list[1] in vares and type(vares[direct_list[1]]) == bool:
			...
		else:
			vares[direct_list[1]] = temp[1]
	else:
		vares[direct] = True

# функция распарсивает строку условия на элементы
def parse_condition(vares, direct):
	operand_list = re.split(r'!|=|\(|\)|\bor\b|\band\b|\bnot\b|<|>', direct)
	for i in operand_list:
		if len(operand_list) > 1:
			i = i.strip()
			if i != "" and (not i in vares):
				vares[i] = i
		elif not i in vares:
			vares[i] = False

# функция, которая проверяет, выполняется ли условие
def met_condition(vares, direct):
	result = dict()
	parse_condition(vares, direct)
	# следующий цикл формирует условие с действительными значениями вместо элементов
	for var in vares:
		trim_var = re.search(r'\b'+var+r'\b', direct)
		if (var in direct) and (trim_var != None):
			if type(vares[var]) == str:
				direct = direct.replace(var, "'" + str(vares[var]) + "'")
			else:
				direct = direct.replace(var, str(vares[var]))
	direct = direct.replace("''", "'")
	direct = direct.replace('""', '"')
	direct = "out=(True if " + direct + " else False)"
	exec(direct, result)
	return result['out']

# функция, которая правильно открывает блок условия
def open_condition(command, condition, args):
	i_list = re.split(r'\s+', command.strip())
	prev_args = args['if']
	for i in i_list:
		if i == "exclude" and condition == True:
			prev_args["include"] = args["include"]
			args["include"] = False
		elif i == "exclude" and condition == False:
			prev_args["include"] = args["include"]
			args["include"] = True
		elif i == "include" and condition == False:
			prev_args["include"] = args["include"]
			args["include"] = False
		elif i == "include" and condition == True:
			prev_args["include"] = args["include"]
			args["include"] = True
		elif i == "nopp" and condition == True:
			prev_args["pp"] = args["pp"]
			args["pp"] = False
		elif i == "nopp" and condition == False:
			prev_args["pp"] = args["pp"]
			args["pp"] = True
		elif i == "savecomm" and condition == True:
			prev_args["savecomm"] = args["savecomm"]
			args["savecomm"] = True
		elif i == "savecomm" and condition == False:
			prev_args["savecomm"] = args["savecomm"]
			args["savecomm"] = False
	args["openif"] = True

# функция, которая правильно закрывает условие
def close_condition(args):
	prev_args = args["if"]
	args["include"] = prev_args["include"]
	args["pp"] = prev_args["pp"]
	args["savecomm"] = prev_args["savecomm"]


def replace_args(arguments, args):
	""" функция переназначающая локальные для текущего файла режимы из глобальных """
	if "include" in args:
		arguments["include"] = args["include"]
	if "pp" in args:
		arguments["pp"] = args["pp"]
	if "savecomm" in args:
		arguments["savecomm"] = args["savecomm"]

def find_speccom_scope(string_line:str):
	maximal = len(string_line)+1
	mini_data_base = {
		"scope-name": [
			'simple-speccom',
			'strong-speccom',
			'apostrophe',
			'quote',
			'brace-open',
			'brace-close'
		],
		"scope-regexp":
		[
			re.search(r'!@(?!\<)', string_line),
			re.search(r'!@<', string_line),
			re.search(r'"', string_line),
			re.search(r"'", string_line),
			re.search(r'\{', string_line),
			re.search(r'\}', string_line)
		],
		"scope-instring":
		[]
	}
	for i, string_id in enumerate(mini_data_base['scope-name']):
		match_in = mini_data_base['scope-regexp'][i]
		mini_data_base['scope-instring'].append(
			string_line.index(match_in.group(0)) if match_in is not None else maximal)
	minimal = min(mini_data_base['scope-instring'])
	if minimal != maximal:
		i = mini_data_base['scope-instring'].index(minimal)
		scope_type = mini_data_base['scope-name'][i]
		scope_regexp_obj = mini_data_base['scope-regexp'][i]
		scope = scope_regexp_obj.group(0)
		q = string_line.index(scope)
		prev_line = string_line[0:q]
		post_line = string_line[q+len(scope):]
		return scope_type, prev_line, scope_regexp_obj, post_line
	else:
		return None, '', re.match(r'^\s*$', ''), string_line


def pp_string(text_lines, string, args):
	""" обработка строки. Поиск спецкомментариев """
	result = string
	if args["include"] == True:
		# обработка
		if args["pp"] == True and args["savecomm"] == False:
			result = ""
			while len(string) > 0:
				scope_type, prev_text, scope_regexp_obj, post_text = find_speccom_scope(string)
				if args["openquote"] == False:
					if scope_type == "apostrophe":
						args["openquote"] = True
						args["quote"] = "apostrophes"
						result += prev_text + scope_regexp_obj.group(0)
						string = post_text
					elif scope_type == 'quote':
						args["openquote"] = True
						args["quote"] = "quotes"
						result += prev_text + scope_regexp_obj.group(0)
						string = post_text
					elif scope_type == "brace-open":
						args["openquote"] = True
						args["quote"] = "brackets"
						result += prev_text + scope_regexp_obj.group(0)
						string = post_text
					elif scope_type == "brace-close":
						result += prev_text + scope_regexp_obj.group(0)
						string = post_text
					elif scope_type == "simple-speccom":
						# если это не удаляющий комментарий, но специальный
						# необходимо удалить его из строки
						if post_text.count('"') % 2 == 0 and post_text.count("'") % 2 == 0 and (not post_text.count('{') > post_text.count('}')):
							# только если мы имеем дело с чётным числом кавычек, можно убирать спецкомментарий
							result += prev_text
							result = re.sub(r'\s*?\&\s*?$', '', result) + '\n'
							if re.match(r'^\s*?$',result) != None:
								result = ""
							break
						else:
							# если в спецкомментарии присутствуют открытые кавычки, оставляем такой спецкомментарий
							result += prev_text + scope_regexp_obj.group(0)
							string = post_text
					elif scope_type == "strong-speccom":
						# если это удаляющий комментарий
						if post_text.count('"') % 2 == 0 and post_text.count("'") % 2 == 0 and (not post_text.count('{') > post_text.count('}')):
							# только если мы имеем дело с чётным числом кавычек, можно убирать спецкомментарий
							result="" # строка удаляется из списка
							break
						else:
							# если в спецкомментарии присутствуют открытые кавычки, оставляем такой спецкомментарий
							result += prev_text + scope_regexp_obj.group(0)
							string = post_text
					else:
						result += string
						break
				else:
					if scope_type == "apostrophe" and args["quote"] == "apostrophes":
						args["openquote"] = False
						args["quote"] = ""
						result += prev_text + scope_regexp_obj.group(0)
						string = post_text
					elif scope_type == "quote" and args["quote"] == "quotes":
						args["openquote"] = False
						args["quote"] = ""
						result += prev_text + scope_regexp_obj.group(0)
						string = post_text
					elif scope_type == "brace-close" and args["quote"] == "brackets":
						args["openquote"]=False
						args["quote"] = ""
						result += prev_text + scope_regexp_obj.group(0)
						string = post_text
					elif scope_type != None:
						result += prev_text + scope_regexp_obj.group(0)
						string = post_text
					else:
						result += string
						break
	elif args["include"] == False:
		# строки исключаются
		result = ""
	if result != "":
		if re.match(r'^\s*?$', result) != None and args["openquote"] == False:
			result = ""
		text_lines.append(result)

# основная функция
def pp_this_file(file_path, args, variables = None):
	""" эта функция будет обрабатывать файл и возвращать результат после препроцессинга """
	with open(file_path, 'r', encoding='utf-8') as pp_file:
		file_lines = pp_file.readlines() # получаем список всех строк файла
	result_lines = pp_this_lines(file_lines, args, variables)
	return ''.join(result_lines)

def pp_this_lines(file_lines:list, args:dict, variables:dict = None) -> list:
	# стандартные значения, если не указаны:
	if variables is None: variables = { "Initial": True, "True": True, "False": False }
	result_text = [] # результат обработки: список строк
	arguments = {
		# словарь режимов (текущих аргументов):
		"include": True, # пока включен этот режим, строки добавляются в результат
		"pp": True, # пока включен этот режим, строки обрабатываются парсером
		"openif": False, # отметка о том, что открыт блок условия
		"savecomm": False, # отметка о том, что не нужно удалять специальные комментарии
		"openquote": False, # отметка, что были открыты кавычки
		"quote": "", # тип открытых кавычек
		"if": { "include": True, "pp": True, "savecomm": False } # список инструкций до выполнения блока условий
	}
	replace_args(arguments, args) # если переданы какие-то глобальные аргументы, подменяем текущие на глобальные
	# перебираем строки в файле
	for line in file_lines:
		command = re.match(r'^!@pp:', line) # проверяем является ли строка командой
		if command == None:
			# если это не команда, обрабатываем строку
			pp_string(result_text, line, arguments)
		else:
			# если это команда, распарсим её
			comm_list = re.split(r':', line)
			if arguments["pp"]:
				# только при включенном препроцессоре выполняются все команды
				# проверяем, что за команда
				if strfind(r'^on\n$', comm_list[1]) != "":
					# на данном этапе данная команда уже не актуальна
					pp_string(result_text, line, arguments)
				elif strfind(r'^off\n$', comm_list[1]) != "":
					# на данном этапе данная команда уже не актуальна
					pp_string(result_text, line, arguments)
				elif strfind(r'^savecomm\n$', comm_list[1]) != "":
					# данная команда включает режим сохранения спецкомментариев
					arguments["savecomm"] = True
				elif strfind(r'^nosavecomm\n$', comm_list[1]) != "":
					# данная команда выключает режим сохранения спецкомментариев
					arguments["savecomm"] = False
				elif strfind(r'^endif\n$', comm_list[1]) != "":
					# закрываем условие
					close_condition(arguments)
				elif strfind(r'^var\(.*?\)', comm_list[1]) != "":
					# если мы имеем дело с присвоением значения переменной
					direct = get_direct(comm_list[1], 'var') # получаем содержимое скобок
					add_variable(variables, direct) # добавляем метку в словарь
				elif strfind(r'^if\(.*?\)', comm_list[1]) != "":
					# если мы имеем дело с проверкой условия
					direct = get_direct(comm_list[1], 'if') # получаем содержимое скобок
					condition = met_condition(variables, direct) # проверяем условие
					open_condition(comm_list[2], condition, arguments)
				else:
					# если идёт запись !@pp: отдельной строкой без команды, данная просто не включается в выходной файл
					pass
			else:
				# при отключенном препроцессоре выполняется только команда endif
				if strfind(r'^endif\n$', comm_list[1]) != "":
					# закрываем условие.
					close_condition(arguments)
				else:
					result_text.append(line)
	if arguments["openif"] == True:
		close_condition(arguments)
	return result_text

# main
def main():
	args={"include":True, "pp":True, "savecomm":False} # глобальные значения
	source_file_path = "../../[disdocs]/example_project/[pp-test]/pptest.qsps"
	output_file_path = "../../[disdocs]/example_game/pp-test/pptest.qsps"
	output_text = pp_this_file(source_file_path, args)
	with open(output_file_path, 'w', encoding='utf-8') as fp:
		fp.write(output_text)

if __name__ == '__main__':
    main()