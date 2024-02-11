import sublime
import sublime_plugin

import os
import json

from .qsps_to_qsp import NewQspsFile

class QspWorkspace:
	def __init__(self, all_workspaces:dict) -> None:
		self.all_ws = all_workspaces # dict of all workspaces
		# microbase of locations
		self.loc_names = [] # names of location [str]
		self.loc_regions = [] # regions of locs initiate list[start, end]
		self.loc_places = [] # file path, where is qsp_locs [str]
		# microbase of files_path
		self.files_paths = [] # all files in project

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

	def refresh_files_paths(self) -> None:
		""" refresh files mb in ws """
		project_folder = QspWorkspace.get_cur_pf()
		if project_folder is None:
			return None
		project_data = sublime.active_window().project_data()
		old = self.files_paths[:]
		new = []
		folders = project_data['folders']
		for pf in folders:
			if os.path.abspath(os.path.join(project_folder, pf['path'])) == project_folder:
				pf_ = project_folder
			else:
				pf_ = pf['path']
			if os.path.commonprefix([project_folder, pf_]) == '':
				break
			new.extend(get_files_list(pf_))
		self.files_paths = new
		old_set = set(old)
		new_set = set(new)
		to_del = list(old_set - new_set)
		to_add = list(new_set - old_set)
		for path in to_del:
			self.del_all_locs_by_place(os.path.relpath(path, project_folder))
		for path in to_add:
			relpath = os.path.relpath(path, project_folder)
			for loc_name, loc_region in NewQspsFile(path).get_qsplocs():
				self.add_loc(loc_name, loc_region, relpath)

	def refresh_locs_from_symbols(self, view) -> None:
		"""	Return list of QSP-locations created on this view """
		current_qsps, project_folder = self.get_main_pathes(view)
		if current_qsps is None or project_folder is None:
			return None
		qsps_relpath = os.path.relpath(current_qsps, project_folder)
		self.del_all_locs_by_place(qsps_relpath)
		for s in view.symbols():
			region, name = s
			if name.startswith('Локация: '):
				self.add_loc(name[9:], [region.begin(), region.end()], qsps_relpath)

	def get_json_struct(self) -> dict:
		qsp_ws_out = { 'locations': {}, 'files_paths': self.files_paths }
		qsp_locs = qsp_ws_out['locations']
		for i, path in enumerate(self.loc_places):
			if not path in qsp_locs: qsp_locs[path] = []
			qsp_locs[path].append([self.loc_names[i], self.loc_regions[i]])
		return qsp_ws_out

	def save_to_file(self, project_folder=None) -> None:
		project_folder = self.get_cur_pf(project_folder)
		if project_folder is None:
			return None
		qsp_workspace = self.get_json_struct()
		with open(os.path.join(project_folder, 'qsp-project-workspace.json'), "w", encoding="utf-8") as ws_file:
			json.dump(qsp_workspace, ws_file, indent=4)

	def get_locs(self):
		return zip(self.loc_names, self.loc_regions, self.loc_places)

	@staticmethod
	def get_cur_pf(project_folder:str=None): # -> str or None
		""" Get path of current project folder if exist """
		if not project_folder is None:
			return project_folder
		argv = sublime.active_window().extract_variables()
		return (argv['folder'] if 'folder' in argv else None)

	@staticmethod
	def get_main_pathes(view:sublime.View):
		""" Get current qsps-file path and project_folder path """
		current_qsps = view.file_name()
		project_folder = QspWorkspace.get_cur_pf()
		return current_qsps, project_folder

	@staticmethod
	def get_all_qsplocs(view:sublime.View, all_workspaces:dict=None) -> list:
		"""
			Extract all qsp-locations from ws.
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
			qsp_ws.refresh_locs_from_symbols(view)
			all_qsplocs = qsp_ws.get_locs()
		else:
			# if ws dont exist in dict of wss
			for s in view.symbols():
				region, name = s
				if name.startswith('Локация: '):
					all_qsplocs.append((name[9:], [region.begin(), region.end()], ''))
		return all_qsplocs

	@staticmethod
	def get_qsplbls(view:sublime.View, exclude_inputting:sublime.Region=None) -> list: # View, Region -> list
		"""
			Return list of QSP-labels created on this view
		"""
		qsp_labels = []
		for s in view.symbols():
			region, name = s
			if exclude_inputting is None or region != exclude_inputting:
				if name.startswith('Метка: '):
					qsp_labels.append(name[7:])
		return qsp_labels
