import sublime
import sublime_plugin

import os
import json
import hashlib

from .qsps_to_qsp import NewQspsFile
from .pad import QSpyFuncs as qspf

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
		# microbase of variables
		self.local_vars = []
		self.global_vars = []
		self.global_vars_names = set()

	def add_loc(self, name:str, region:tuple, place:str) -> int:
		""" Добавление локации в воркспейс """
		self.loc_names.append(name)
		self.loc_regions.append(region)
		self.loc_places.append(place)
		return len(self.loc_names)-1

	def get_dupl_locs(self):
		""" получаем локации с одинаковыми названиями """
		_cr_loc = lambda x: [self.loc_names[x], self.loc_regions[x], self.loc_places[x]]
		qsp_locs = []
		for i, loc_name in enumerate(self.loc_names):
			u = i + 1
			l = _cr_loc(i)
			while u < len(self.loc_names) and loc_name in self.loc_names[u:]:
				u = self.loc_names.index(loc_name, u)
				if not l is None:
					qsp_locs.append(l)
					l = None
				qsp_locs.append(_cr_loc(u))
				u += 1
		return qsp_locs

	def add_qsps(self, file_path:str, file_hash:str) -> int:
		self.files_paths.append(file_path)
		self.files_hashs.append(file_hash)
		return len(self.files_paths)-1

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

	def extract_from_file(self, ws_path:str) -> None:
		"""
			Extract data from file in ws. ws_path - is full path to ws-file.
			WARNING!!! All proves of project folder and exist of
			ws-file must be done prev call this function
		"""
		with open(ws_path, "r", encoding="utf-8") as ws_file:
			qsp_ws = json.load(ws_file)
		if len(self.loc_names)>0:
			self.__init__()
			print('Error: QSP WORKSPACE already initialised!!!')
		for path, qsp_locs in qsp_ws['locations'].items():
			for name, region in qsp_locs:
				self.add_loc(name, region, path)
		# print(ws_path, 'files_paths' in qsp_ws)
		for path, md5 in qsp_ws['files_paths'].items():
			self.files_paths.append(path)
			self.files_hashs.append(md5)

	def refresh_files(self) -> None:
		""" refresh files mb in ws """
		project_folder = QspWorkspace.get_cur_pf()
		if project_folder is None:	return None
		folders = sublime.active_window().folders()
		old = set(self.get_files(project_folder)) # abs-paths + hashs
		files = []
		for f in folders:
			pf_ = self.absing_path(project_folder, f)
			files.extend(qspf.get_files_list(pf_))
		new = set()
		for f in files:
			pf_ = self.absing_path(project_folder, f)
			new.add((pf_, self.get_hash(pf_))) # abs-paths + hashs
		to_del = list(old - new)
		to_add = list(new - old)
		try:
			to_del_paths, to_del_hashs = [], []
			if len(to_del)>0:
				print('unpack this')
				to_del_paths, to_del_hashs = zip(*to_del)
		except ValueError as e:
			print(to_del, str(e))
			sublime.message_dialog('Error RAISE in this moment!!!')
			raise e
			
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
				self.add_qsps(new_path, self.get_hash(new_path))

		# replace old files
		for old_path, md5 in to_del:
			path = self.reling_path(project_folder, old_path)
			self.del_all_locs_by_place(path)
			self.del_qsps(path)

	def refresh_md5(self, path:str, project_folder:str) -> None:
		""" Refreshing md5 of file by path """
		relpath = self.reling_path(project_folder, path)
		if relpath in self.files_paths:
			i = self.files_paths.index(relpath)
			self.files_hashs[i] = self.get_hash(path)

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

	def refresh_qsplocs(self, view:sublime.View, current_qsps:str, project_folder:str) -> None:
		"""	Return list of QSP-locations created on this view """
		if not current_qsps is None:
			qsps_relpath = self.reling_path(project_folder, current_qsps)
		else:
			qsps_relpath = ''
		self.del_all_locs_by_place(qsps_relpath)
		for s in view.symbol_regions():
			if s.name.startswith('Локация: '):
				self.add_loc(s.name[9:], [s.region.begin(), s.region.end()], qsps_relpath)

	def get_json_struct(self) -> dict:
		qsp_ws_out = { 'locations': {}, 'files_paths': {} }
		qsp_locs = qsp_ws_out['locations']
		qsp_files = qsp_ws_out['files_paths']
		for i, path in enumerate(self.loc_places):
			if path == '': continue
			if not path in qsp_locs: qsp_locs[path] = []
			qsp_locs[path].append([self.loc_names[i], self.loc_regions[i]])
		for i, path in enumerate(self.files_paths):
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

	def get_files(self, project_folder:str=None) -> list: # list of tuples!
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
			for i, string_id in enumerate(mini_data_base['sprtr-name']):
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
				break
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
		return current_qsps, project_folder # path:str|None, path:str|None

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
		current_qsps, project_folder = QspWorkspace.get_main_pathes(view)
		if project_folder in all_workspaces:
			# if ws exist in dict of wss
			qsp_ws = all_workspaces[project_folder]
			qsp_ws.refresh_qsplocs(view, current_qsps, project_folder)
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
		if os.path.commonprefix([project_folder, other_path]) != '':
			return os.path.relpath(other_path, project_folder)
		else:
			return other_path