import sys
import os

# standart funcs for

def safe_mk_fold(new_path:str) -> None:
	""" Safe make dir with making all chain of dir """
	if not os.path.isdir(new_path):
		os.makedirs(new_path)

def write_error_log(error_text:str) -> None:
	""" Write message in console. """
	print(error_text)

def get_files_list(folder:str, filters:list=None) -> list:
	""" Create list of files in folder and includes folders. """
	if filters is None: filters = ['.qsps', '.qsp-txt', '.txt-qsp']
	build_files = []
	for abs_path, _, files in os.walk(folder):
		for file in files:
			sp = os.path.splitext(file)
			if not filters or (sp[1] in filters):
				build_files.append(os.path.join(abs_path, file))
	if not build_files:
		write_error_log(f'[200] Folder is empty. Prove path «{folder}».')
	return build_files

def compare_paths(path1:str, path2:str):
	"""	Compare two paths and return tail relative to shared folder. """
	start = os.path.commonprefix([path1, path2])
	path1 = os.path.relpath(path1, start)
	path2 = os.path.relpath(path2, start)
	return path1, path2

def search_project_folder(path:str, print_error:bool=True, project_file:str='qsp-project.json') -> str:
	"""
		Find project-file and return folder path whith project.
		In other return None.
	"""
	project_folder = (os.path.split(path)[0] if os.path.isfile(path) else path)
	while not os.path.isfile(os.path.join(project_folder, project_file)):
		if os.path.ismount(project_folder):
			if print_error:
				write_error_log(f"[202] not found 'qsp-project.json' file for this project. Prove path {path}.")
			return None
		project_folder = os.path.split(project_folder)[0]
	else:
		return project_folder

# функция возвращает словарь команд, в зависимости от полученных от системы аргументов
def parse_args(qsp_mode:str, point_file:str) -> dict:
	"""
		Returns modes dictionary, based on systems arguments.
	"""
	args = {}

	args['build'] = (qsp_mode in ('--br', '--build'))
	args['run'] = (qsp_mode in ('--br', '--run'))	

	if os.path.isfile(point_file):
		args['point_file'] = os.path.abspath(point_file)
	else:
		args['point_file'] = os.path.join(os.getcwd(), sys.argv[0])

	return args

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

def is_path_in_project_folders(path:str, project_folders:list) -> bool:
	"""
		Prove that path is existed in project_folders.
	"""
	all_pathes = project_folders[:]
	all_pathes.append(path)
	if None in all_pathes: return False
	for folder in project_folders:		
		try:
			if os.path.commonpath([path, folder]) == folder:
				return True
		except ValueError as e: # если файлы лежат на разных дисках. TODO: убрать вывод в консоль
			write_error_log(f'[203] Different pathes of folder and file. Error "{str(e)}". path: {path}. folder: {folder}.')
			continue
	return False

def log(string:str,) -> None:
	log_file_path = 'D:\\my\\GameDev\\QuestSoftPlayer\\projects\\JAD\\qsp-workspace-log.log'
	with open(log_file_path, 'a', encoding='utf-8') as fp:
		fp.write(string + '\n')

if __name__=="__main__":
	...