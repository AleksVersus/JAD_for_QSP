import re

base_code = """! base
*P '1111''777777'
"345-2345-3444"
ACT 'Действие', 'image/i.png':
	*pl '2'
END

act 'Действие 2', 'image/i.png':
	*pl '2'
end
! end base

! BASE
ACT 'Действие3', 'image/i.png':
	*pl '2'
END

act 'Действие 4', 'image/i.png':
	*pl '2'
end

*PL     'string new

string last' & 'ignored'
! END BASE

! BASE

*P"4"
ACT "Действие 5", "image/i.png":
	*pl '2'
END

act 'Действие 6', 'image/i.png':
	*pl '2'
end
! END BASE"""

def split_base() -> None:
	""" Split base code to description and actions """
	# base_code = ''.join(self.base_code)
	def _parse_string(qsps_line:str, mode:dict) -> None:
		""" Parse opened string for location code """
		for char in qsps_line:
			if mode['open-string'] == '':
				# string not open
				if char in ('"', '\'', '{'):
					mode['open-string'] = char
			else:
				if char in ('"', '\'') and mode['open-string'][-1] == char:
					mode['open-string'] = mode['open-string'][:-1]
				elif char == '}' and mode['open-string'][-1] == '{':
					mode['open-string'] = mode['open-string'][:-1]
				elif char == '{':
					mode['open-string'] += char

	def _string_to_desc(line:str, mode:dict, opened:str) -> None:
		nonlocal base_description
		need = ('"', "'") # ожидаем кавчки
		valid = (" ", "\t") # допустимые символы
		new_line = '\n' if opened in ('open-pl', 'open-implicit') else ''
		for i, char in enumerate(line):
			if not mode[opened]:
				# пока не открыт набор в описание
				if char in need:
					# нашли ожидаемый символ, открываем набор
					mode['open-string'] = char
					mode[opened] = True
				elif not char in valid:
					# найден недопустимый символ
					break
			elif mode[opened]:
				if char != mode['open-string']:
					base_description += char
				elif (i < len(line)-1 and line[i+1] == mode['open-string']):
					continue
				elif (i > 0 and line[i-1] == mode['open-string']):
					# символ кавычки экранирован,значит его тоже можно в описание
					base_description += char
				else: # char = open-string и соседние символы другие
					# закрываем набранное
					base_description += new_line
					mode[opened] = False
					mode['open-string'] = ''
					break		

	def _all_modes_off(mode:dict) -> None:
		return (mode['open-string'] == ''
			and not mode['open-pl']
			and not mode['open-p']
			and not mode['open-implicit']
			and not mode['action-name']
			and not mode['action-image']
			and not mode['action-code'])

	def _empty_buffer() -> dict:
		return {
			'name': '',
			'image': '',
			'code': ''
		}
	base_code_lines = base_code.splitlines(keepends=True)
	mode = {
		'open-string': '',
		'open-pl': False,
		'open-p': False,
		'open-implicit': False,
		'action-name': False,
		'action-image': False,
		'action-code': False,
	}
	base_description = ''
	base_act_buffer = _empty_buffer()
	base_actions = []

	for line in base_code_lines:
		if _all_modes_off(mode):
			if re.match(r'^("|\')', line):
				_string_to_desc(line, mode, 'open-implicit')
			elif re.match(r'^\*PL\b', line):
				# строка с командой вывода текста
				_string_to_desc(line[3:], mode, 'open-pl')					
			elif re.match(r'^\*P\b', line):
				_string_to_desc(line[2:], mode, 'open-p')
			elif  re.match(r'^ACT\b', line):
				need = ('"', "'") # ожидаем кавчки
				valid = (" ", "\t") # допустимые символы
				stage = 'need name'
				for i, char in enumerate(line[3:]):
					if mode['action-name']:
						# название найдено, набираем
						if char != mode['open-string']:
							base_act_buffer['name'] += char
						elif (i < len(line)-1 and line[i+1] == mode['open-string']):
							continue
						elif (i > 0 and line[i-1] == mode['open-string']):
							# символ кавычки экранирован,значит его тоже можно в описание
							base_act_buffer['name'] += char
						else: # char = open-string и соседние символы другие
							# закрываем набранное
							mode['action-name'] = False
							mode['open-string'] = ''
							stage = 'need prev image'
							need = (",", ':')
							valid = (" ", "\t")
					elif mode['action-image']:
						# изображение найдено, набираем
						if char != mode['open-string']:
							base_act_buffer['image'] += char
						elif (i < len(line)-1 and line[i+1] == mode['open-string']):
							continue
						elif (i > 0 and line[i-1] == mode['open-string']):
							# символ кавычки экранирован,значит его тоже можно в описание
							base_act_buffer['image'] += char
						else: # char = open-string и соседние символы другие
							# закрываем набранное
							mode['action-image'] = False
							mode['open-string'] = ''
							stage = 'need code'
							need = (':')
							valid = (" ", "\t")
					elif stage == 'need name':
						# поиск названия действия
						if char in need:
							# найдено вхождение строки
							mode['open-string'] = char
							mode['action-name'] = True
						elif not char in valid:
							# недопустимый символ, игнорируем действие
							break
					elif stage == 'need prev image':
						# ищем запятую перед вторым аргументом
						if char == ",":
							stage = "need image"
							need = ("'", '"')
							valid = (" ", "\t")
							continue
						elif char == ":":
							# набор названия и изображения кончился, набираем код
							mode['action-code'] = True
							break
						elif not char in valid:
							# действие кривое, прерываем
							base_act_buffer = _empty_buffer()
							break
					elif stage == 'need image':
						if char in need:
							mode['action-image'] = True
							mode['open-string'] = char
						elif not char in valid:
							break
					elif stage == 'need code':
						if char == ':':
							mode['action-code'] = True
							break
						elif not char in valid:
							mode['action-code'] = False
							base_act_buffer = _empty_buffer()
							break
			else:
				_parse_string(line, mode)
		elif mode['open-pl']:
			_string_to_desc(line, mode, 'open-pl')
		elif mode['open-p']:
			_string_to_desc(line, mode, 'open-p')
		elif mode['open-implicit']:
			_string_to_desc(line, mode, 'open-p')
		elif mode['action-code']:
			if mode['open-string'] == '' and re.match(r'^END\b', line):
				# найдено окончание кода, закрываем
				mode['action-code'] = False
				base_actions.append(base_act_buffer)
				base_act_buffer = _empty_buffer()
			else:
				base_act_buffer['code'] += line
				_parse_string(line, mode)
		elif mode['action-image'] or mode['action-name']:
			# переносы строк в названиях и изображениях базовых действий недопустимы
			mode['action-name'] = False
			mode['action-image'] = False
			base_act_buffer = _empty_buffer()
			_parse_string(line, mode)
		elif mode['open-string']:
			_parse_string(line, mode)


	# print('base_description: ', f'"{base_description}"')
	# print(base_actions)

if __name__ == '__main__':
	split_base()
