from .function import parse_args
from .function import search_project_folder
from .function import get_files_list
from .function import safe_mk_fold
from .function import clear_locname

class QSpyFuncs:
	"""
		Pad for extract functions in namespace.
	"""
	@staticmethod
	def parse_args(arguments:dict) -> dict:
		return parse_args(arguments)

	@staticmethod
	def search_project_folder(path:str, print_error:bool=True) -> str:
		return search_project_folder(path, print_error)

	@staticmethod
	def get_files_list(folder:str, filters:list=None) -> list:
		return get_files_list(folder, filters)

	@staticmethod
	def safe_mk_fold(new_path:str) -> None:
		safe_mk_fold(new_path)

	@staticmethod
	def clear_locname(loc_name:str) -> str:
		return clear_locname(loc_name)
