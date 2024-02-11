import sublime
import sublime_plugin

import os
import json
import hashlib

from .qsps_to_qsp import NewQspsFile

class QspWorkspace:
	def __init__(self, all_workspaces:dict) -> None:
		self.all_ws = all_workspaces # dict of all workspaces
		# microbase of locations
		self.loc_names = [] # names of location [str]
		self.loc_regions = [] # regions of locs initiate list[start, end]
		self.loc_places = [] # file path, where is qsp_locs [str]
		# microbase of files_path
		self.files_paths = [] # all files in project (rel or abs pathes)
		self.files_hashs = []

	def add_loc(self, name:str, region:tuple, place:str) -> int:
		""" Добавление локации в воркспейс """
		self.loc_names.append(name)
		self.loc_regions.append(region)
		self.loc_places.append(place)
		return len(self.loc_names)-1

	def del_loc_by_place(self, loc_place:str) -> None:
		""" del location by place """
		if loc_place in self.loc_places:
			i = self.loc_places.index(loc_place)
			del self.loc_places[i]
			del self.loc_names[i]
			del self.loc_regions[i]

	def del_all_locs_by_place(self, loc_place:str) -> None:
		""" del all locations by place """
		while loc_place in self.loc_places:
			i = self.loc_places.index(loc_place)
			del self.loc_places[i]
			del self.loc_names[i]
			del self.loc_regions[i]

	def extract_from_file(self, project_folder:str=None) -> None:
		""" extract data from file in ws """
		if project_folder is None:
			return None
		ws_path = os.path.join(project_folder, 'qsp-project-workspace.json')
		if not os.path.isfile(ws_path):
			return None
		with open(ws_path, "r", encoding="utf-8") as ws_file:
			qsp_ws = json.load(ws_file)
		if len(self.loc_names)>0:
			self.__init__()
			print('Error: QSP WORKSPACE already initialised!!!')
		for path, qsp_locs in qsp_ws['locations'].items():
			for name, region in qsp_locs:
				self.add_loc(name, region, path)
		self.files_paths = qsp_ws['files_paths']

	def refresh_files(self) -> None:
		""" refresh files mb in ws """
		project_folder = QspWorkspace.get_cur_pf()
		if project_folder is None:	return None
		folders = sublime.active_window().folders()
		old = set(self.get_files(project_folder)) # abs-paths + hashs
		files = []
		for f in folders:
			pf_ = self.absing_path(project_folder, f)
			files.extend(get_files_list(pf_))
		new = set()
		for f in files:
			pf_ = self.absing_path(project_folder, f)
			new.add((pf_, self.get_hash(pf_))) # abs-paths + hashs
		to_del = list(old - new)
		to_add = list(new - old)
		to_del_paths, to_del_hashs = zip(to_del)
		# replace on new paths
		for new_path, md5 in to_add[:]:
			if md5 in to_del_hashs:
				i = to_del_hashs.index(md5)
				f = to_del_paths[i]
				old_path = self.reling_path(project_folder, f)
				self.replace_qsps(old_path, new_path)
				to_del.pop(i)
				to_del_hashs.pop(i)
				to_del_paths.pop(i)
			else:
				path = self.reling_path(project_folder, new_path)
				for loc_name, loc_region in NewQspsFile(new_path).get_qsplocs():
					self.add_loc(loc_name, loc_region, path)
		# replace old files
		for old_path, md5 in to_del:
			path = self.reling_path(project_folder, old_path)
			self.del_all_locs_by_place(path)
			self.del_qsps(path)

	def replace_qsps(self, old_path:str, new_path:str) -> None:
		if old_path in self.files_paths:
			i = self.files_paths.index(old_path)
			self.files_paths[i] = new_path
		while True:
			if old_path in self.loc_places:
				i = self.loc_places.index(old_path)
				self.loc_places[i] = new_path
			else:
				break

	def del_qsps(self, path:str) -> None:
		if path in self.files_paths:
			i = self.files_paths.index(path)
			del self.files_paths[i]
			del self.files_hashs[i]


	def refresh_qsplocs(self, view) -> None:
		"""	Return list of QSP-locations created on this view """
		current_qsps, project_folder = self.get_main_pathes(view)
		if current_qsps is None or project_folder is None:
			return None
		qsps_relpath = os.path.relpath(current_qsps, project_folder)
		self.del_all_locs_by_place(qsps_relpath)
		for s in view.symbol_regions():
			if s.name.startswith('Локация: '):
				self.add_loc(s.name[9:], [s.region.begin(), s.region.end()], qsps_relpath)

	def get_json_struct(self) -> dict:
		qsp_ws_out = { 'locations': {}, 'files_paths': {} }
		qsp_locs = qsp_ws_out['locations']
		qsp_files = qsp_ws_out['files_paths']
		for i, path in enumerate(self.loc_places):
			if not path in qsp_locs: qsp_locs[path] = []
			qsp_locs[path].append([self.loc_names[i], self.loc_regions[i]])
		for i, path in self.files_paths:
			qsp_files[path] = self.files_hashs[i]
		return qsp_ws_out

	def save_to_file(self, project_folder=None) -> None:
		project_folder = self.get_cur_pf(project_folder)
		if project_folder is None:
			return None
		qsp_workspace = self.get_json_struct()
		with open(os.path.join(project_folder, 'qsp-project-workspace.json'), "w", encoding="utf-8") as ws_file:
			json.dump(qsp_workspace, ws_file, indent=4)

	def get_locs(self) -> list: #list of tuples!
		""" Return List of qsp-locations from ws. See .get_all_qsplocs """
		return zip(self.loc_names, self.loc_regions, self.loc_places)

	def get_files(self, project folder:str=None) -> list: # list of tuples!
		""" Return list if qsps-files from ws:
			list[
				tuple(path_of_file:str, hash_of_file:str)
			]
		"""
		if not project_folder is None:
			l = lambda f: self.absing_path(project_folder, f)
			files_paths = list(map(l, self.files_paths))
		else:
			files_paths = self.files_paths
		return zip(files_paths, self.files_hashs)

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
	def get_cur_pf(project_folder:str=None): # -> str or None
		""" Get path of current project folder if exist """
		if not project_folder is None:
			return project_folder
		folders = sublime.active_window().folders()
		return (folders[0] if len(folders)>0 else None)

	@staticmethod
	def get_main_pathes(view:sublime.View):
		""" Get current qsps-file path and project_folder path """
		current_qsps = view.file_name()
		project_folder = QspWorkspace.get_cur_pf()
		return current_qsps, project_folder

	@staticmethod
	def get_all_qsplocs(view:sublime.View, all_workspaces:dict=None, only=None) -> list:
		"""
			Extract all qsp-locations from ws and view.
			Return →
			list[tuple(
				loc_name:str,
				loc_region:list[begin:int, end:int],
				loc_place:path_to_qsps_file:str
			)]
		"""
		if all_workspaces is None: all_workspaces = {}
		all_qsplocs = []
		project_folder = QspWorkspace.get_cur_pf()
		if project_folder in all_workspaces:
			# if ws exist in dict of wss
			qsp_ws = all_workspaces[project_folder]
			qsp_ws.refresh_qsplocs(view)
			all_qsplocs = (qsp_ws.loc_names if only == 'names' else qsp_ws.get_locs())
		else:
			# if ws dont exist in dict of wss
			for s in view.symbol_regions():
				if s.name.startswith('Локация: '):
					if only == 'names':
						all_qsplocs.append(s.name[9:])
					else:
						all_qsplocs.append((s.name[9:], [s.region.begin(), s.region.end()], ''))
		return all_qsplocs

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
			get project_folder - abs path, other_path: rel o abs path
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
		if os.path.commonprefix(project_folder, other_path) != '':
			return os.path.relpath(other_path, project_folder)
		else:
			return other_path