import sys
import os

from . import pp

def safe_mk_fold(new_path:str) -> None:
	""" Safe make dir with making all chain of dir """
	if not os.path.isdir(new_path):
		os.makedirs(new_path)

def write_error_log(error_text:str) -> None:
	""" Write message in console. """
	print(error_text)

def get_files_list(folder, filters=None):
	"""
		Create list of files in folder and includes folders.
	"""
	if filters is None: filters = [".qsps",'.qsp-txt','.txt-qsp']
	build_files=[]
	tree=os.walk(folder)
	for abs_path, folders, files in tree:
		for file in files:
			sp = os.path.splitext(file)
			if len(filters)==0 or (sp[1] in filters):
				build_files.append(os.path.join(abs_path, file))
	if len(build_files)==0:
		write_error_log(f'[201] Folder is empty. Prove path «{folder}».')
	return build_files

def compare_paths(path1, path2):
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
			write_error_log(f"[202] File don't exist. Prove path {file_path}.")
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
				write_error_log(f"[203] not found 'project.json' file for this project. Prove path {error}.")
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

def exit_files(game_path:str) -> list: # list[abs_paths]
	"""
		On input QSP-file's path,
		on output QSP-file's abs.path and temporary txt-file's abs path.
	"""
	exit_qsp = os.path.abspath(game_path)
	exit_txt = os.path.abspath(os.path.splitext(game_path)[0]+".txt")
	return [exit_qsp, exit_txt]

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

def need_point_file(root, start_file, point_file):
	"""
		Unloading conditions.
		If not `start` in root or not exist start-file, 
		and running file is qsp, return True, other False.
	"""
	cond = all((
		(not "start" in root) or (not os.path.isfile(start_file)),
		os.path.splitext(point_file)[1]==".qsp"
		))
	return (True if cond else False)

def get_standart_project(point_file, player):
	"""
		Unloading code.
		Create standart text of project-file in json-format.
	"""
	game_name = os.path.splitext(os.path.split(point_file)[1])[0]
	return ''.join([
		'{\n\t"project":\n\t[\n\t\t{\n\t\t\t"build":".\\', game_name,
		'.qsp",\n\t\t\t"files":\n\t\t\t[\n\t\t\t\t{"path":"',
		point_file, '"}\n\t\t\t]\n\t\t}\n\t],\n\t"start":".\\',
		game_name, '.qsp",\n\t"player":"', player, '"\n}'
		])

def print_builder_mode(build, run):
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

if __name__=="__main__":
	pass