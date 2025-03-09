import os
import subprocess

from . import function as qsp
from .qsps_to_qsp import NewQspsFile
from .pp import pp_this_lines
# import time

class ModuleQSP():

	def __init__(self):

		self.src_qsps_file = []		# list[SrcQspsFile]

		self.output_qsp = None		# path of output QSP-file (module)
		self.output_txt = None		# path of temp file in txt2gam format

		# self.code_system = 'utf-8'
		self.converter = 'qsps_to_qsp' # converter qsps -> QSP
		self.converter_param = ''	# string of parameters for converting

		self.qsps_code = []			# all strings of module code
		# self.start_time = start_time
	
	def set_converter(self, converter:str='qsps_to_qsp', args:str='') -> None:
		""" set path to converter, or converter name """
		self.converter = converter
		self.converter_param = args

	def extend_by_file(self, file_path:str) -> None: # file_path:abs_path of file
		""" Add SrcQspsFile by file-path """
		if os.path.isfile(file_path):
			self.src_qsps_file.append(SrcQspsFile(file_path))
		else:
			qsp.write_error_log(f'[203] File don\'t exist. Prove path {file_path}.')

	def extend_by_folder(self, folder_path:str) -> None:
		""" Add SrcQspsFile-objs by folder-path """
		if not os.path.isdir(folder_path):
			qsp.write_error_log(f'[204] Folder don\'t exist. Prove path {folder_path}.')
			return None
		for el in qsp.get_files_list(folder_path):
			file_path = os.path.abspath(el) # TODO: if el is abspath - del absing path of el
			self.extend_by_file(file_path)

	def extend_by_src(self, src_strings:list) -> None:
		""" Add SrcQspsFile by qsps-src-code strings """
		self.src_qsps_file.append(SrcQspsFile(file_path=None, src_strings=src_strings))

	def set_exit_files(self, game_path:str) -> None:
		"""
			On input QSP-file's path,
			on output QSP-file's abs.path and temporary txt-file's abs path.
		"""
		self.output_qsp = os.path.abspath(game_path)
		self.output_txt = os.path.splitext(self.output_qsp)[0]+".txt"

	def choose_code_system(self) -> str:
		return ('utf-8' if self.converter == 'qsps_to_qsp' else 'utf-16-le')


	def preprocess_qsps(self, pponoff:str, pp_markers:dict) -> None:
		""" 
			На данном этапе у нас есть объекты класса SrcQspsFile, которые включают в себя список
			строк для каждого файла, т.е. цикл чтения уже завершён. Теперь мы можем обработать эти
			виртуальные файлы, прогнав их через препроцессор.

			pponoff — управление препроцессором main
			pp_markers — переменные и метки
		"""
		# text = "" # выходной текст
		for src in self.src_qsps_file:
			if pponoff == 'Hard-off':
				# text_file = src.read() + '\r\n' # файл не отправляется на препроцессинг
				...
			elif pponoff == 'Off':
				first_string = src.get_string(0)
				second_string = src.get_string(1)
				if "!@pp:on\n" in (first_string, second_string):
					arguments = {"include": True, "pp": True, "savecomm": False}
					# файл отправляется на препроцессинг
					src.preprocess(arguments, pp_markers)
				# text_file = src.read() + "\r\n"
			elif pponoff == 'On':
				first_string = src.get_string(0)
				second_string = src.get_string(1)
				if not "!@pp:off\n" in (first_string, second_string):
					arguments = {"include":True, "pp":True, "savecomm":False}
					src.preprocess(arguments, pp_markers)
				# text_file = src.read() + '\r\n'
			# text += src.read() + '\r\n'

	def read(self) -> str:
		""" Get outer text of module """
		text = ""
		for src in self.src_qsps_file:
			text += src.read() + '\r\n'
		return text

	def save_temp_file(self):
		# если папка не создана, нужно её создать
		path_folder = os.path.split(self.output_txt)[0]
		if not os.path.exists(path_folder):
			os.makedirs(path_folder)
		text = self.read()
		code_system = self.choose_code_system()
		# необходимо записывать файл в кодировке utf-16le, txt2gam версии 0.1.1 понимает её
		text = text.encode(code_system, 'ignore').decode(code_system,'ignore')
		with open(self.output_txt, 'w', encoding=code_system) as file:
			file.write(text)

	def extract_qsps(self):
		for src in self.src_qsps_file:
			self.qsps_code.extend(src.get_strings())

	def convert(self, save_temp_file:bool) -> None:
		# start_time = time.time()
		if self.converter == 'qsps_to_qsp':
			qsps_file = NewQspsFile()
			qsps_file.set_file_source(self.qsps_code)
			# print(f'Module.newqsps {time.time() - start_time}, {time.time() - self.start_time}')
			qsps_file.split_to_locations()
			qsps_file.to_qsp()
			# print(f'Module.convert {time.time() - start_time}, {time.time() - self.start_time}')
			qsps_file.save_to_file(self.output_qsp)
			# print(f'Module.save_qsp {time.time() - start_time}, {time.time() - self.start_time}')
			if save_temp_file: self.save_temp_file()
			# print(f'Module.temp {time.time() - start_time}, {time.time() - self.start_time}')
		else:
			self.save_temp_file()
			_run = [self.converter, self.output_txt, self.output_qsp, self.converter_param]
			subprocess.run(_run, stdout=subprocess.PIPE)
			if not save_temp_file:
				os.remove(self.output_txt)

class SrcQspsFile():

	def __init__(self, file_path:str, src_strings:list=None) -> None:

		self.file_path = file_path
		self.src_strings = src_strings

		if file_path is not None:
			with open(file_path, 'r', encoding='utf-8') as fp:
				self.src_strings = fp.readlines()

	def read(self) -> str:
		""" Return of src in text-format """
		return ''.join(self.src_strings)

	def get_string(self, number:int) -> str:
		""" return string of src """
		return self.src_strings[number]

	def get_strings(self) -> list:
		return self.src_strings

	def preprocess(self, args:dict, pp_variables:dict) -> None:
		""" Препроцессинг файла. Пока что используется внешний файл	"""
		self.src_strings = pp_this_lines(self.src_strings, args, pp_variables)