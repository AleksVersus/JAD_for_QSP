import sublime			# type: ignore

import os
import json
from typing import (Union, List, Tuple)
import hashlib

from .qsps_to_qsp import NewQspsFile
from . import function as qsp
from . import const as const

class QspWorkspace:
	def __init__(self, all_workspaces:dict) -> None:
		self.all_ws = all_workspaces # dict of all workspaces
		# microbase of locations
		self.locs = {
			'names': [],	# names of location [str]
			'regions': [],	# regions of locs initiate tuple[start, end]
			'places': [],	# file path, where is qsp_locs [str]
			'hashes': []	# all datas in tuple
		}
		# microbase of qsps-file's pathes
		self.qsps_files = {
			'pathes': [],	# all files in project (abs pathes)
			'hashes': []	# md5
		}
		# microbase of variables
		self.local_vars = []	# list[sublime.Region]
		self.global_vars = []	# list[sublime.Region]
		self.global_vars_names = set()  # set[variables names]
		# modes
		self.save_temp_files = True
		self.markers = {
			'on_pre_close_project': False
		}

	def _log(self, string:str) -> None:
		if self.save_temp_files:
			qsp.log(string, self.save_temp_files)

# --------------------------------- qsp-locations mb functions ---------------------------------

	def add_loc(self, name:str, region:tuple, place:str) -> None:
		""" Add new qsp-location to workspace """
		if not (name, region, place) in self.locs['hashes']:
			# one index for all fields
			self.locs['names'].append(name)
			self.locs['regions'].append(region)
			self.locs['places'].append(place)
			self.locs['hashes'].append((name, region, place))

	def replace_locs(self, old_path:str, new_path:str) -> None:
		""" Change place of qsp-locations. """
		while old_path in self.locs['places']:
			i = self.locs['places'].index(old_path)
			self.locs['places'][i] = new_path
			self.loc_hash_update(i)

	def del_loc_by_index(self, i:int) -> None:
		""" Delete the qsp-location from workspace by index"""
		if i < 0 or i > len(self.locs['names'])-1: return None
		del self.locs['names'][i]
		del self.locs['regions'][i]
		del self.locs['places'][i]
		del self.locs['hashes'][i]

	def del_all_locs_by_place(self, loc_place:Union[str, int]) -> None:
		""" del all locations by place. loc_place - path at file with qsp_location """
		while loc_place in self.locs['places']:
			i = self.locs['places'].index(loc_place)
			self.del_loc_by_index(i)

	def loc_hash_update(self, i:int) -> None:
		""" Обновляем хэш локации """
		self.locs['hashes'][i] = (
			self.locs['names'][i],
			self.locs['regions'][i],
			self.locs['places'][i]
		)

	def get_locs(self) -> list:
		return self.locs['hashes'].copy()
	
	def get_locs_names(self) -> list:
		"""	Extract all qsp-location's names. """
		return self.locs['names'].copy()

	def refresh_qsplocs(self, view:sublime.View, current_qsps:str) -> None:
		"""	Refresh list of QSP-locations created on this view """
		qsps_path = (view.id() if current_qsps is None else current_qsps) # abs_path
		self.del_all_locs_by_place(qsps_path)
		for s in view.symbol_regions():
			if s.name.startswith('Локация: '): # TODO: привязка к тому, что символ начинается с Локация не очень удобна!
				self.add_loc(s.name[9:], (s.region.begin(), s.region.end()), qsps_path)

	def clear_old_qsplocs(self, views:List[sublime.View]) -> None:
		""" Delete locations from WS, if this views don't exist. """
		view_ids = [v.id() for v in views]
		for place in self.locs['places']:
			if isinstance(place, int) and not place in view_ids:
				self.del_all_locs_by_place(place)

	def locs_dupl(self) -> list: # list[tuples(name, region, place)] *[1]
		""" Get qsp-locations with duplicate names. """
		qsp_locs = [] # list[tuples(name, region, place)]
		exclude_hashes = []
		for i, loc_hash in enumerate(self.locs['hashes']):
			loc_name, _, _ = loc_hash
			if (not loc_hash in exclude_hashes) and (loc_name in self.locs['names'][i+1:]):
				qsp_locs.append(loc_hash)
				exclude_hashes.append(loc_hash)
				u = i + 1
				while u < len(self.locs['hashes']) and loc_name in self.locs['names'][u:]:
					u = self.locs['names'].index(loc_name, u)
					qsp_locs.append(self.locs['hashes'][u]) # add duplicate to out list
					exclude_hashes.append(self.locs['hashes'][u])
					u += 1 # search next location
		return qsp_locs

# --------------------------------- qsp-locations mb functions ---------------------------------

# ----------------------------------- qsps-files mb functions -----------------------------------

	def get_qsps_files(self) -> list: # list of tuples!
		"""
			Return list of qsps-files from WS:
			list[tuples(path_of_file:str, hash_of_file:str)]
		"""
		# all pathes in list of pathes are abs. Dont need use absing func.
		return list(zip(self.qsps_files['pathes'], self.qsps_files['hashes']))

	def add_qsps_file(self, qsps_file_path:str, qsps_file_hash:str) -> int:
		""" Add qsps-file to WS """
		self.qsps_files['pathes'].append(qsps_file_path)
		self.qsps_files['hashes'].append(qsps_file_hash)

	def del_qsps_file(self, path:str) -> None:
		if path in self.qsps_files['pathes']:
			i = self.qsps_files['pathes'].index(path)
			del self.qsps_files['pathes'][i]
			del self.qsps_files['hashes'][i]

	def replace_qsps_file(self, old_path:str, new_path:str) -> None:
		""" When replace the phisically file, or rename it,
		this func replace old file by new in WS. """
		if old_path in self.qsps_files['pathes']:
			i = self.qsps_files['pathes'].index(old_path)
			self.qsps_files['pathes'][i] = new_path

	def refresh_qsps_files(self, window_folders:list) -> None:
		""" refresh files mb in ws """
		old = set(self.get_qsps_files()) # set[tuple(abs-path, hash)]
		files_pathes = []
		for f in window_folders:
			files_pathes.extend(qsp.get_files_list(f))
		new = set()
		for f in files_pathes:
			new.add((f, self.get_hash(f))) # set[tuple(abs-path, hash)]
		to_del = list(old - new)
		to_add = list(new - old)
		to_del_paths, to_del_hashs = [], []
		if len(to_del)>0:
			to_del_paths, to_del_hashs = zip(*to_del) # tuples
		to_del_hashs = list(to_del_hashs)
		to_del_paths = list(to_del_paths)
		# replace on new paths
		for new_path, md5 in to_add[:]: # to_add = list[tuples(file_path, file_hash)]
			if md5 in to_del_hashs:
				i = to_del_hashs.index(md5)
				old_path = to_del_paths[i]
				self.replace_qsps_file(old_path, new_path)
				self.replace_locs(old_path, new_path)
				del to_del[i]
				del to_del_hashs[i]
				del to_del_paths[i]
			else:
				qsps_file = NewQspsFile()
				qsps_file.read_from_file(new_path)
				qsps_file.split_to_locations()
				for loc_name, loc_region in qsps_file.get_qsplocs():
					# str, tuple(start, end)
					self.add_loc(loc_name, loc_region, new_path)
				self.add_qsps_file(new_path, md5)

		# replace old files
		for old_path, md5 in to_del:
			self.del_all_locs_by_place(old_path)
			self.del_qsps_file(old_path)

	def refresh_md5(self, qsps_file_path:str) -> None:
		""" Refreshing md5 of file by path """
		if qsps_file_path in self.qsps_files['pathes']:
			i = self.qsps_files['pathes'].index(qsps_file_path)
			self.qsps_files['hashes'][i] = self.get_hash(qsps_file_path)

	def qsps_file_is_exist(self, qsps_file_path:str) -> bool:
		""" Prove qsps-file is exist in WS """
		return qsps_file_path in self.qsps_files['pathes']

	def qsps_files_number(self) -> int:
		"""
			Return number of qsps-files in WS.
		"""
		return len(self.qsps_files['pathes'])

# ----------------------------------- qsps-files mb functions -----------------------------------

# ---------------------------------------- WS functions ----------------------------------------

	def extract_from_file(self, ws_file_path:str) -> None:
		"""
			Extract data from file to WS. ws_file_path - is abspath to ws-json file.
			WARNING!!! All proves of project folder and exist of
			ws-file must be done prev call this function!
		"""
		with open(ws_file_path, "r", encoding="utf-8") as fp:
			ws_json = json.load(fp) # get json struct ws from file

		if len(self.locs['hashes']) > 0:
			self.__init__()
			qsp.write_error_log(const.QSP_ERROR_MSG.WS_ALREADY_INIT)

		for place, qsp_locs in ws_json['locations'].items():
			# ws_json['locations'] = dict[abs_path: qsp_locs]
			# TODO: на данном этапе разработки все пути в файле абсолютные, однако абсолютные пути
			# TODO: должны оставаться только у файлов, хранящихся на других дисках!!!
			# qsp_locs = list[qsp_loc];
			# qsp_loc = list[name, list[start_point, end_point]]
			for name, region in qsp_locs:
				self.add_loc(name, tuple(region), place)

		for path, md5 in ws_json['files_paths'].items():
			self.qsps_files['pathes'].append(path)
			self.qsps_files['hashes'].append(md5)

	def get_json_struct(self) -> dict:
		qsp_ws_out = { 'locations': {}, 'files_paths': {} }
		qsp_locs_out = qsp_ws_out['locations']
		qsp_files_out = qsp_ws_out['files_paths']
		for qsp_loc in self.locs['hashes']:
			qsps_file_path = qsp_loc[2]
			if isinstance(qsps_file_path, int): continue
			if not qsps_file_path in qsp_locs_out: qsp_locs_out[qsps_file_path] = []
			qsp_locs_out[qsps_file_path].append([qsp_loc[0], qsp_loc[1]])
		for i, qsps_file_path in enumerate(self.qsps_files['pathes']):
			# TODO: здесь часть путей должна преобразовываться в относительные
			# перед возвращением в виде json-структуры.
			qsp_files_out[qsps_file_path] = self.qsps_files['hashes'][i]
		return qsp_ws_out

	def save_to_file(self, project_folder:str=None) -> None:
		"""
			Save WS in json-file. project_folder must be exist!
		"""
		if project_folder is None: return None
		json_ws = self.get_json_struct()
		if not 'locations' in json_ws or not json_ws['locations']: return None
		ws_json_path = os.path.join(project_folder, 'qsp-project-workspace.json')
		with open(ws_json_path, "w", encoding="utf-8") as ws_fp:
			json.dump(json_ws, ws_fp, indent=4, ensure_ascii=False)

	def refresh_from_views(self, windows_views:List[sublime.View], window_folders:List[str]) -> None:
		"""
			Refresh untitled views and opened files in WS.
		"""
		_conditional_is_true = (lambda x, y:
			x is None or qsp.is_path_in_project_folders(x, y))
		for view in windows_views:
			if QspWorkspace.view_syntax_is_wrong(view): continue
			current_qsps = view.file_name()
			if _conditional_is_true(current_qsps, window_folders):
				self.refresh_qsplocs(view, current_qsps)
				self.refresh_vars(view)
		self.clear_old_qsplocs(windows_views) # clear locs from untitled views

	def close_project(self) -> None:
		self.markers['on_pre_close_project'] = True

	def project_is_closing(self) -> bool:
		return self.markers['on_pre_close_project']

# ---------------------------------------- WS functions ----------------------------------------


# ---------------------------------- variables mb function in WS ----------------------------------
	def refresh_vars(self, view:sublime.View) -> None:
		def _find_overlap_main(start_find):
			maximal = view.size()+1
			mini_data_base = {
				"sprtr-name": [
					'assign',
					'while',
					'brace'
				],
				"sprtr-region":
				[
					view.find('=', start_find, flags=1+2),
					view.find('while', start_find, flags=1+2),
					view.find('}', start_find, flags=1+2)
				],
				"sprtr-instring":
				[]
			}
			for i, _ in enumerate(mini_data_base['sprtr-name']):
				region = mini_data_base['sprtr-region'][i]
				mini_data_base['sprtr-instring'].append(
					region.begin() if region.begin()!=-1 else maximal)
			minimal = min(mini_data_base['sprtr-instring'])
			if minimal != maximal:
				i = mini_data_base['sprtr-instring'].index(minimal)
				sprtr_type = mini_data_base['sprtr-name'][i]
				sprtr_region = mini_data_base['sprtr-region'][i]
				return sprtr_type, sprtr_region
			else:
				return None, None

		kw_regions = view.find_all('local', flags=2+4)
		vars_regions = []
		_safe_f = lambda x, y, z: view.match_selector(y.begin(),x) and y.begin()<z
		for r in kw_regions:
			if not view.match_selector(r.begin(), 'keyword.declaration.variables.qsp'):
				continue
			# not use 'local' in string and comment scopes
			start_region = r.end()
			end_line = view.line(r).end()
			end_region = end_line
			start_find = start_region
			# print(view.substr(sublime.Region(start_region, end_region)))
			while start_find < end_line:
				sprtr_type, sprtr_region = _find_overlap_main(start_find)
				if sprtr_type == 'assign':
					if _safe_f('keyword.operator.one-sign.qsp', sprtr_region, end_line):
						end_region = sprtr_region.begin()-1
						break
					else:
						start_find = sprtr_region.end()
				elif sprtr_type == 'while':
					if _safe_f('keyword.control.qsp', sprtr_region, end_line):
						end_region = sprtr_region.begin()-1
						break
					else:
						start_find = sprtr_region.end()
				elif sprtr_type == 'brace':
					if _safe_f('avs_brace_end', sprtr_region, end_line):
						end_region = sprtr_region.begin()-1
						break
					else:
						start_find = sprtr_region.end()
				else:
					end_region = end_line
					break
				# break
			vars_regions.append(sublime.Region(start_region, end_region))
			# print(view.substr(sublime.Region(start_region, end_region)))
		if len(vars_regions) == 0: return None

		user_variable = r'\$?[A-Za-zА-Яа-я_][\w\.]*'
		# uv_regions = view.find_all(user_variable, 2)
		# start = 0
		# for uv in uv_regions[0:25]:
		# 	f = view.find(user_variable, start, 2)
		# 	start = f.end()
		# 	print(view.substr(f))
		# 	print(view.substr(uv))
		start_point = vars_regions[0].begin()
		edge_point = vars_regions[0].end()
		end_point = vars_regions[-1].end()
		i = 1
		u = 0
		local_vars = []
		while start_point < end_point and not u > 999:
			u += 1
			find_var = view.find(user_variable, start_point, flags=2)
			if find_var.begin()!=-1 and find_var.begin() < edge_point:
				# print(start_point, view.substr(find_var), find_var)
				for var in view.find_all(view.substr(find_var).replace('$', r'\$')+r'\b', flags=2):
					if not find_var.begin() > var.begin() and view.match_selector(var.begin(), 'meta.user-variables.qsp'):
						# print(var, view.substr(var))
						local_vars.append(var)
			start_point = find_var.end()+1
			if start_point > edge_point:
				if i < len(vars_regions):
					start_point = vars_regions[i].begin()
					edge_point = vars_regions[i].end()
					i += 1
				else:
					break
		self.local_vars = local_vars # list[sublime.Region]
		global_vars = []
		for var in view.find_all(user_variable, flags=2):
			if not var in local_vars and view.match_selector(var.begin(), 'meta.user-variables.qsp'):
				global_vars.append(var)
				self.global_vars_names.add(view.substr(var))
		self.global_vars = global_vars

	def get_local_vars(self) -> list:
		return self.local_vars

	def get_global_vars(self) -> list:
		return self.global_vars

# ---------------------------------- variables mb function in WS ----------------------------------

	@staticmethod
	def get_hash(file_path:str) -> str:
		md5_hash = hashlib.new('md5')
		with open(file_path, 'rb') as file:
			while True:
				data = file.read(1024)
				if not data:
					break
				md5_hash.update(data)
		return md5_hash.hexdigest()

	@staticmethod
	def project_folder(view:sublime.View) -> Union[str, None]:
		""" Get project folder from view. """
		folders = view.window().folders()
		return (folders[0] if folders else None)

	@staticmethod
	def current_project_folder() -> Union[str, None]:
		""" Get path of current project folder if exist. """
		folders = sublime.active_window().folders()
		return (folders[0] if folders else None)

	@staticmethod
	def get_main_pathes(view:sublime.View) -> Tuple[Union[str, None], Union[str, None]]:
		""" Get current qsps-file path and project_folder path. """
		current_qsps = view.file_name()
		folders = view.window().folders()
		project_folder = (folders[0] if folders else None)
		return current_qsps, project_folder # path:str|None, path:str|None

	@staticmethod
	def get_qsplbls(view:sublime.View, exclude_inputting:sublime.Region=None) -> list: # View, Region -> list
		"""
			Return list of QSP-labels created on this view
		"""
		qsp_labels = []
		for s in view.symbol_regions():
			if exclude_inputting is None or s.region != exclude_inputting:
				if s.name.startswith('Метка: '):
					qsp_labels.append(s.name[7:])
		return qsp_labels

	@staticmethod
	def absing_path(project_folder:str, other_path:str) -> str: # -> abs other path
		"""
			get project_folder - abs path, other_path: rel or abs path
			return abs path of otherpath
		"""
		if os.path.abspath(os.path.join(project_folder, other_path)) == project_folder:
			return project_folder
		elif os.path.abspath(other_path) == other_path:
			return other_path
		else:
			return os.path.abspath(os.path.join(project_folder, other_path))

	@staticmethod
	def reling_path(project_folder:str, other_path:str) -> str: # rel other path, or abs if not possible
		if os.path.commonprefix([project_folder, other_path]) != '':
			return os.path.relpath(other_path, project_folder)
		else:
			return other_path

	@staticmethod
	def view_syntax_is_wrong(view:sublime.View) -> bool:
		""" Prove QSP syntax! """
		vs = view.syntax()
		return (True if (vs is None or vs.name != 'QSP') else False)