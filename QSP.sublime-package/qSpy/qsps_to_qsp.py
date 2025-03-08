# Converter qsps-files (only UTF-8) into game files `.qsp`.
# stand `file_path` and run script for getting QSP-format file.

import os
import re
import concurrent.futures

from function import (del_first_pref)
# import time

# constants:
QSP_CODREMOV = 5 # const of cyphering
# regexps:
LOCATION_START = re.compile(r'^\#\s*(.+)$')
LOCATION_END = re.compile(r'^\-\-(.*)$')
BASE_OPEN = re.compile(r'^\! BASE$')
BASE_CLOSE = re.compile(r'^\! END BASE$')
PRINT_STRING = re.compile(r'^\*P\b')
PRINT_LINE = re.compile(r'^\*PL\b')
ACTION_START = re.compile(r'^ACT\b')
ACTION_END = re.compile(r'^END\b')
IMPLICIT_OPERATOR = re.compile(r'^("|\')')

class NewQspLocation():
	"""
		qsp-locations from qsps-file
	"""
	def __init__(self, name:str, code:list=None) -> None:
		""" Initialise QSP-location """
		self.name:str = name							# location name qsps
		self.name_region:tuple = ()	# tuple[start, end] # location name in regions
		self.code:list = ([] if code == None else code)	# location code qsps
		self.base_code:list = []	# base code (qsps lines of base acts and desc)
		self.base_description:str = '' # concatenate strings of base descs in text-format
		self.base_actions:list = [] # list of base actions dicts
			# actions format
			# {
			# 	'image': '',
			# 	'name': '',
			#	'code': []
			# }
		self.decode_name:str = ''	# decode in QSP-format location name
		self.decode_desc:str = ''	# decode in QSP-format location description
		self.decode_actions:list = [] # list of decode in QSP-format location actions
		self.decode_code:str = ''	# decode in QSP-format location code		

	def change_name(self, name:str) -> None:
		""" Set location name """
		self.name = name

	def change_region(self, region:tuple) -> None:
		""" Set location name region """
		self.name_region = region

	def add_code_string(self, code_string:str) -> None:
		self.code.append(code_string)

	def change_code(self, code:list) -> None:
		""" Set location code. """
		self.code = code

	def decode(self) -> None:
		""" Decode parts of location. """
		self.decode_name = NewQspsFile.decode_qsps_line(self.name)
		self.extract_base()
		self.split_base()
		self.decode_desc = NewQspsFile.decode_qsps_line(self.base_description)
		self.decode_code = NewQspsFile.decode_qsps_line((''.join(self.code))[:-1])
		for action in self.base_actions:
			decode_action = ''
			decode_action += NewQspsFile.decode_qsps_line(action['image']) + '\n'
			decode_action += NewQspsFile.decode_qsps_line(action['name']) + '\n'
			action_code = ''.join(del_first_pref(action['code']))
			decode_action += NewQspsFile.decode_qsps_line(action_code[:-1]) + '\n'
			self.decode_actions.append(decode_action)

	def get_qsp(self) -> str:
		""" Get QSP-format location """
		qsp = []
		qsp.append(self.decode_name + '\n')
		qsp.append(self.decode_desc + '\n')
		qsp.append(self.decode_code + '\n')
		qsp.append(NewQspsFile.decode_qsps_line(str(len(self.decode_actions))) + '\n')
		qsp.extend(self.decode_actions)
		return qsp

	def extract_base(self) -> None:
		""" Extract base from location code """
		mode = {
			'open-base': False,
			'open-string': '',
		}
		base_lines = []
		for i, qsps_line in enumerate(self.code[:]):
			if mode['open-base']:
				self.code[i] = None # remove from other code
				if mode['open-string'] == '' and BASE_CLOSE.search(qsps_line):	
					mode['open-base'] = False
					break
				base_lines.append(qsps_line)
				NewQspsFile.parse_string(qsps_line, mode)
				continue
			if mode['open-string'] == '' and BASE_OPEN.search(qsps_line):
				mode['open-base'] = True
				self.code[i] = None
			else:
				NewQspsFile.parse_string(qsps_line, mode)

		if base_lines: self.base_code = base_lines
		self.code = [line for line in self.code if line is not None]

	def split_base(self) -> None:
		""" Split base code to description and actions """
		def _string_to_desc(line:str, mode:dict, opened:str) -> None:
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
						self.base_description += char
					elif (i < len(line)-1 and line[i+1] == mode['open-string']):
						continue
					elif (i > 0 and line[i-1] == mode['open-string']):
						# символ кавычки экранирован,значит его тоже можно в описание
						self.base_description += char
					else: # char = open-string и соседние символы другие
						# закрываем набранное
						self.base_description += new_line
						mode[opened] = False
						mode['open-string'] = ''
						break

		def _string_to_act(line:str, mode:dict, base_act_buffer:dict) -> None:
			need = ('"', "'") # ожидаем кавчки
			valid = (" ", "\t") # допустимые символы
			stage = 'need name'
			for i, char in enumerate(line):
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
						base_act_buffer = _empty_buffer()
						break
				elif stage == 'need code':
					if char == ':':
						mode['action-code'] = True
						break
					elif not char in valid:
						mode['action-code'] = False
						base_act_buffer = _empty_buffer()
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
				'code': []
			}
		
		mode = {
			'open-string': '',
			'open-pl': False,
			'open-p': False,
			'open-implicit': False,
			'action-name': False,
			'action-image': False,
			'action-code': False}

		base_act_buffer = _empty_buffer()

		for line in self.base_code:
			if _all_modes_off(mode):
				if IMPLICIT_OPERATOR.match(line):
					_string_to_desc(line, mode, 'open-implicit')
				elif PRINT_LINE.match(line):
					# строка с командой вывода текста
					_string_to_desc(line[3:], mode, 'open-pl')					
				elif PRINT_STRING.match(line):
					_string_to_desc(line[2:], mode, 'open-p')
				elif  ACTION_START.match(line):
					_string_to_act(line[3:], mode, base_act_buffer)
				else:
					NewQspsFile.parse_string(line, mode)
			elif mode['open-pl']:
				_string_to_desc(line, mode, 'open-pl')
			elif mode['open-p']:
				_string_to_desc(line, mode, 'open-p')
			elif mode['open-implicit']:
				_string_to_desc(line, mode, 'open-implicit')
			elif mode['action-code']:
				if mode['open-string'] == '' and ACTION_END.match(line):
					# найдено окончание кода, закрываем
					mode['action-code'] = False
					self.base_actions.append(base_act_buffer.copy())
					base_act_buffer = _empty_buffer()
				else:
					base_act_buffer['code'].append(line)
					NewQspsFile.parse_string(line, mode)
			elif mode['action-image'] or mode['action-name']:
				# переносы строк в названиях и изображениях базовых действий недопустимы
				mode['action-name'] = False
				mode['action-image'] = False
				base_act_buffer = _empty_buffer()
				NewQspsFile.parse_string(line, mode)
			elif mode['open-string']:
				NewQspsFile.parse_string(line, mode)

class NewQspsFile():
	"""	qsps-file, separated in locations """
	def __init__(self) -> None:
		"""	initialise """
		# main fields:
		self.locations_count = 0		# location count for set at file
		self.locations = []				# list[NewQspLocation]
		self.locations_id = {}			# dict[locname:locnumber]
		self.src_strings = []			# all strings of file
		self.line_offsets = []
		self.converted_strings:list = []	# output converted strings

		# files fields
		self.input_file = ''	# abspath of qsps-file
		self.output_folder = ''	# output folder name
		self.file_name = ''		# file name without extension
		self.output_file = ''	# output gamefile path

	def set_input_file(self, input_file:str) -> None:
		""" Set input file and pathes of outputs """
		self.input_file = os.path.abspath(input_file)
		self.output_folder, file_full_name = os.path.split(self.input_file)
		self.file_name = os.path.splitext(file_full_name)[0]
		self.output_file = os.path.join(self.output_folder, self.file_name+".qsp")
		
	def set_file_source(self, file_strings:list=None) -> None:
		""" Set source strings of file """
		if file_strings:
			self.src_strings = file_strings[:]
			self.line_offsets = []
			offset = 0
			for line in self.src_strings:
				self.line_offsets.append(offset)
				offset += len(line)

	def convert_file(self, input_file:str) -> None:
		""" Convert qsps-file to qsp-file """
		if os.path.isfile(input_file):
			self.read_from_file(input_file)
			self.split_to_locations()
			self.to_qsp()
			self.save_to_file()
		
	def read_from_file(self, input_file:str=None) -> None:
		""" Read qsps-file and set source strings """
		if input_file and os.path.isfile(input_file):
			self.set_input_file(input_file)
		if self.input_file:
			offset = 0
			with open(self.input_file, 'r', encoding='utf-8') as fp:
				for line in fp:
					self.src_strings.append(line)
					self.line_offsets.append(offset)
					offset += len(line)
		else:
			print(f'[801] File {self.input_file} is not exist.')

	def save_to_file(self, output_file:str=None) -> None:
		""" Save qsps-text to file. """
		if not output_file:
			output_file = self.output_file
		with open(output_file, 'w', encoding='utf-16le') as file:
			file.writelines(self.converted_strings)

	def split_to_locations(self) -> None:
		""" Split source strings to locations """
		mode = {
			'location-name': '',
			'open-string': ''}
		location = None
		for i, qsps_line in enumerate(self.src_strings):
			if mode['location-name'] == '': # open string work only in open location
				match = LOCATION_START.search(qsps_line)
				if match:
					# open location
					locname = match.group(1).replace('\r', '')
					location = NewQspLocation(locname)
					region_start = match.start(1) + self.line_offsets[i]
					region_end = region_start + len(match.group(1).strip())
					location.change_region((region_start, region_end))
					self.append_location(location)
					mode['location-name'] = locname
				else:
					self.parse_string(qsps_line, mode)
			elif mode['open-string'] == '' and LOCATION_END.search(qsps_line):
				# close location
				mode['location-name'] = ''
			else:
				self.parse_string(qsps_line, mode)
				location.add_code_string(qsps_line)

	def append_location(self, location:NewQspLocation) -> None:
		""" Add location in NewQspsFile """
		self.locations.append(location)
		self.locations_id[location.name] = self.locations_count
		self.locations_count += 1

	def to_qsp(self) -> None:
		""" Convert NewQspsFile to QSP-format """
		if self.converted_strings:
			print('[301] Already converted.')
			raise Exception('[301] Already converted.')
		# header of qsp-file
		self.converted_strings.append('QSPGAME\n')
		self.converted_strings.append('qsps_to_qsp SublimeText QSP Package\n')
		self.converted_strings.append(self.decode_qsps_line('No')+'\n')
		self.converted_strings.append(self.decode_qsps_line(str(self.locations_count))+'\n')
		# decode locations
		_decode_location = lambda l: l.decode()
		with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
			for location in self.locations:
				executor.submit(_decode_location, location)
		for location in self.locations:
			self.converted_strings.extend(location.get_qsp())
		# print(f'qsps.converted: {time.time() - start_time}')

	def get_qsplocs(self) -> list:
		""" Return qsp-location for adding to ws """
		qsp_locs = [] # list[list[str, tuple[int, int]]]
		for location in self.locations:
			qsp_locs.append([location.name, location.name_region])
		return qsp_locs

	def print_locations_names(self):
		print('Locations number: '+str(len(self.locations)))
		for location in self.locations:
			print(location.name)

	def print_location(self, name=0):
		if type(name) == int:
			location_name = self.locations[name].name
			location_code = self.locations[name].code
		elif type(name) == str:
			location_name = self.locations[self.locations_id[name]].name
			location_code = self.locations[self.locations_id[name]].code
		if location_name is not None:
			print("'"+location_name+"'")
			print(location_code)

	@staticmethod
	def parse_string(qsps_line:str, mode:dict) -> None:
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

	@staticmethod
	def decode_qsps_line(qsps_line:str='') -> str:
		""" Decode qsps_line to qsp_coded_line """
		exit_line, qsp_codremov = '', QSP_CODREMOV
		for point in qsps_line:
			exit_line += (chr(-qsp_codremov) if ord(point) == qsp_codremov else chr(ord(point) - qsp_codremov))
		return exit_line

	@staticmethod
	def decode_location(code:list) -> str:
		if len(code)>0:
			last_line = code.pop()[:-1]
			exit_line = ''.join(code).replace('\n', '\n')
			return NewQspsFile.decode_qsps_line(exit_line)+NewQspsFile.decode_qsps_line(last_line)
		else:
			return ''
	
	def save_qsps(self, input_file:str=None) -> None:
		if self.input_file is None and input_file is None:
			print('[302] Not input path.')
			raise Exception('[302] Not input path.')
		if input_file is None:
			input_file = self.input_file
		with open(input_file, 'w', encoding='utf-8') as file:
			file.writelines(self.src_strings)

	def save_qsp(self, output_file:str=None) -> None:
		if self.output_file is None and output_file is None:
			print('[303] Not output path.')
			raise Exception('[303] Not output path.')
		if output_file is None:
			output_file = self.output_file
		with open(output_file, 'w', encoding='utf-16le') as file:
			file.writelines(self.converted_strings)

def main():
	qsps = NewQspsFile()
	qsps.convert_file('D:\\game.qsps')

if __name__ == "__main__":
	main()
