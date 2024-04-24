import sys
import subprocess
import os

from . import pp

def safe_mk_fold(new_path:str) -> None:
	""" Safe make dir with making all chain of dir """
	if not os.path.isdir(new_path):
		os.makedirs(new_path)

def write_error_log(error_text:str) -> None:
	""" Write message in console. """
	print(error_text)

def get_files_list(folder:str, filters:list=None) -> list:
	"""
		Create list of files in folder and includes folders.
	"""
	if filters is None: filters = [".qsps",'.qsp-txt','.txt-qsp']
	build_files = []
	tree = os.walk(folder)
	for abs_path, folders, files in tree:
		for file in files:
			sp = os.path.splitext(file)
			if len(filters) == 0 or (sp[1] in filters):
				build_files.append(os.path.join(abs_path, file))
	if len(build_files) == 0:
		write_error_log(f'[200] Folder is empty. Prove path «{folder}».')
	return build_files

def compare_paths(path1:str, path2:str):
	"""
		Compare two paths and return tail relative to shared folder. 
	"""
	start = os.path.commonprefix([path1, path2])
	path1 = os.path.relpath(path1, start)
	path2 = os.path.relpath(path2, start)
	return path1, path2

def gen_files_paths(files_array):
	"""
		Convert dictionary list in paths list.
	"""
	files_paths=[]
	for el in files_array:
		file_path=os.path.abspath(el["path"])
		if os.path.isfile(file_path):
			files_paths.append(file_path)
		else:
			write_error_log(f"[201] File don't exist. Prove path {file_path}.")
	return files_paths

# из списка файлов .qsps .qsp-txt и .txt-qsp создаём файл .txt в фформате TXT2GAM по указанному пути
def construct_file(build_list, new_file, pponoff, pp_markers, code_system='utf-16-le'):
	# получив список файлов, из которых мы собираем выходной файл, делаем следующее
	text="" # выходной текст
	for path in build_list:
		# открываем путь как файл
		with open(path,"r",encoding="utf-8") as file:
			if pponoff=="Hard-off":
				text_file=file.read()+"\r\n" # файл не отправляется на препроцессинг
			elif pponoff=="Off":
				first_string=file.readline()[:]
				second_string=file.readline()[:]
				file.seek(0)
				if first_string=="!@pp:on\n" or second_string=="!@pp:on\n":
					arguments={"include":True, "pp":True, "savecomm":False}
					# файл отправляется на препроцессинг
					text_file = pp.pp_this_file(path, arguments, pp_markers)+'\r\n'
				else:
					text_file=file.read()+"\r\n"
			elif pponoff=="On":
				first_string=file.readline()[:]
				second_string=file.readline()[:]
				file.seek(0)
				if first_string=="!@pp:off\n" or second_string=="!@pp:off\n":
					text_file=file.read()+"\r\n"
				else:
					arguments={"include":True, "pp":True, "savecomm":False}
					text_file=pp.pp_this_file(path,arguments,pp_markers)+'\r\n'
			text+=text_file
	# если папка не создана, нужно её создать
	path_folder=os.path.split(new_file)[0]
	if os.path.exists(path_folder)!=True:
		os.makedirs(path_folder)
	# необходимо записывать файл в кодировке utf-16le, txt2gam версии 0.1.1 понимает её
	text=text.encode(code_system, 'ignore').decode(code_system,'ignore')
	with open(new_file,"w",encoding=code_system) as file:
		file.write(text)

def search_project_folder(path:str, print_error:bool=True) -> str:
	"""
		Find project-file and return folder path whith project.
		In other return None.
	"""
	error = path
	if os.path.isfile(path):
		path = os.path.split(path)[0]
	while not os.path.isfile(os.path.join(path, "project.json")):
		if os.path.ismount(path):
			if print_error:
				write_error_log(f"[202] not found 'project.json' file for this project. Prove path {error}.")
			break
		path = os.path.split(path)[0]
	else:
		return path

# функция возвращает словарь команд, в зависимости от полученных от системы аргументов
def parse_args(arguments):
	"""
		Returns modes dictionary, based on systems arguments.
	"""
	args={}
	for a in arguments:
		if a in ("--buildandrun", "--br", "--b", "--build"):
			args["build"]=True
		if a in ("--buildandrun", "--br", "--r", "--run"):
			args["run"]=True
		if os.path.isfile(a):
			args["point_file"]=os.path.abspath(a)
	if (not "build" in args) and (not "run" in args):
		args["build"]=True
		args["run"]=True
	if not "build" in args:
		args["build"]=False
	if not "run" in args:
		args["run"]=False
	if not "point_file" in args:
		args["point_file"]=os.path.join(os.getcwd(), sys.argv[0])
	return args

def need_project_file(work_dir, point_file, player):
	"""
		Unloading conditions.
		If project-file is not found, and start point file is .qsps, 
		and paths to converter and player are right, return True.
	"""
	cond = all((
		work_dir is None,
		os.path.splitext(point_file)[1] == '.qsps',
		os.path.isfile(player)
		))
	return (True if cond else False)

def get_point_project(point_file:str, player:str) -> dict:
	"""
		Unloading code.
		Create standart text of project-file in json-format.
	"""
	game_name = os.path.splitext(os.path.split(point_file)[1])[0]+'.qsp'
	project_dict = {
		"project":
		[
			{
				"build": game_name,
				"files":
				[
					{"path": point_file}
				]
			}
		],
		"start": game_name,
		"player": player}

def print_builder_mode(build:bool, run:bool) -> None:
	"""
		Unloading code.
		Print builder's work mode.
	"""
	if build and run:
		print("Build and Run Mode")
	elif build:
		print("Build Mode")
	elif run:
		print("Run Mode")

def clear_locname(loc_name:str) -> str:
	""" Clear qsp-location name of extra charges """
	return (loc_name.replace('\\', '\\\\')
		.replace('[', r'\[')
		.replace(']', r'\]')
		.replace('(', r'\(')
		.replace(')', r'\)')
		.replace('.', r'\.')
		.replace('#', r'\#')
		.replace('$', r'\$')
		.replace('&', r'\&')
		.replace('*', r'\*')
		.replace('+', r'\+')
		.replace('-', r'\-')
		.replace('?', r'\?')
		.replace('|', r'\|')
		.replace('/', r'\/'))

class ModuleQSP():

	def __init__(self):

		self.src_qsps_file = []

		self.output_qsp = None
		self.output_txt = None

		self.include_scripts = []

		# self.code_system = 'utf-8'
		self.converter = 'qsps_to_qsp'
		self.converter_param

		self.qsps_code = []

	def extend_by_files(self, files_paths:list) -> None: # file_paths:list of dict {'path': file_path}
		"""
			Convert dictionary list in paths list.
		"""
		for el in files_paths:
			file_path = os.path.abspath(el['path'])
			if os.path.isfile(file_path):
				self.src_qsps_file.append(SrcQspsFile(file_path))
			else:
				write_error_log(f'[203] File don\'t exist. Prove path {file_path}.')

	def extend_by_folder(self, folder_path:str) -> None:
		if not os.path.isdir(folder_path):
			write_error_log(f'[204] Folder don\'t exist. Prove path {folder_path}.')
			return None
		for el in get_files_list(folder_path):
			file_path = os.path.abspath(el)
			if os.path.isfile(file_path):
				self.src_qsps_file.append(SrcQspsFile(file_path))
			else:
				write_error_log(f'[205] File don\'t exist. Prove path {file_path}.')

	def exit_files(self, game_path:str) -> None:
		"""
			On input QSP-file's path,
			on output QSP-file's abs.path and temporary txt-file's abs path.
		"""
		self.output_qsp = os.path.abspath(game_path)
		self.output_txt = os.path.abspath(os.path.splitext(game_path)[0]+".txt")

	def extend_scripts(self, scripts:list) -> None:
		self.include_scripts.extend(scripts)

	def choose_code_system(self) -> str:
		return ('utf-8' if self.converter == 'qsps_to_qsp' else 'utf-16-le')

	def set_converter(self, converter:str='qsps_to_qsp', args:str='') -> None:
		""" set path to converter, or converter name """
		self.converter = converter
		self.converter_param = args

	def preprocess_qsps(self, pponoff:str, pp_markers:dict) -> None:
		""" 
			На данном этапе у нас есть объекты класса SrcQspsFile, которые включают в себя список
			строк для каждого файла, т.е. цикл чтения уже завершён. Теперь мы можем обработать эти
			виртуальные файлы, прогнав их через препроцессор.

			При этом, если используется внешний конвертер,
			то файлы сохраняются в виде временных файлов.
			pponoff — управление препроцессором main
			pp_markers — переменные и метки
		"""
		# text = "" # выходной текст
		for src in self.src_qsps_file:
			if pponoff == 'Hard-off':
				# text_file = src.read() + '\r\n' # файл не отправляется на препроцессинг
				...
			elif pponoff == 'Off':
				first_string = src.string(0)
				second_string = src.string(1)
				if first_string == "!@pp:on\n" or second_string == "!@pp:on\n":
					arguments = {"include": True, "pp": True, "savecomm": False}
					# файл отправляется на препроцессинг
					src.preprocess(arguments, pp_markers)
				# text_file = src.read() + "\r\n"
			elif pponoff == 'On':
				first_string = src.string(0)
				second_string = src.string(1)
				if not (first_string == "!@pp:off\n" or second_string == "!@pp:off\n"):
					arguments = {"include":True, "pp":True, "savecomm":False}
					src.preprocess(arguments, pp_markers)
				# text_file = src.read() + '\r\n'
			# text += src.read() + '\r\n'

	def postprocess_qsps(self, include_scripts:list) -> None:
		# for script in include_scripts:
		# 	subprocess.run([sys.executable, script, exit_txt], stdout=subprocess.PIPE)

		# ПЕрехват принта
		# import sys
		# from subprocess import Popen, PIPE

		# with Popen([sys.executable, '-u', 'child.py'],
		#            stdout=PIPE, universal_newlines=True) as process:
		#     for line in process.stdout:
		#         print(line.replace('!', '#'), end='')
		...

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

class SrcQspsFile():

	def __init_(self, file_path:str) -> None:

		self.file_path = file_path

		with open(file_path, 'r', encoding='utf-8') as fp:
			self.file_strings = fp.readlines()

	def read(self) -> str:
		""" Return of src in text-format """
		return ''.join(self.files_strings)

	def get_string(self, number:int) -> str:
		""" return string of src """
		return self.file_strings[number]

	def preprocess(self, args:dict, pp_variables:dict) -> None:
		"""
			Препроцессинг файла. Пока что используется внешний файл
		"""
		self.file_strings = pp.pp_this_lines(self.file_strings, args, variables)

if __name__=="__main__":
	pass