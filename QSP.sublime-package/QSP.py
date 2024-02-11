import sublime
import sublime_plugin

import sys, os
import re
import json

# Importing my modules from qSpy package.
from .qSpy.function import parse_args
from .qSpy.function import search_project_folder
from .qSpy.function import get_files_list
from .qSpy.function import safe_mk_fold
from .qSpy.builder import BuildQSP
from .qSpy.qsp_to_qsps import QspToQsps
from .qSpy.qsps_to_qsp import NewQspsFile
from .qSpy.qsp_splitter import QspSplitter
from .qSpy.main_cs import FinderSplitter
# Import constants
from .qSpy import const

class QspWorkspace:
	def __init__(self) -> None:
		# microbase of locations
		self.loc_names = [] # names of location [str]
		self.loc_regions = [] # regions of locs initiate list[start, end]
		self.loc_places = [] # file path, where is qsp_locs [str]
		self.files_paths = [] # all files in project

	def hold_init(self, project_folder=None):
		if not project_folder is None:
			self.refresh_files_paths()

	def add_loc(self, name:str, region:tuple, place:str) -> int:
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

	def extract_from_file(self, project_folder=None) -> None:
		if project_folder is None:
			return None
		ws_path = os.path.join(project_folder,'qsp-project-workspace.json')
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
		current_qsps, project_folder = QspWorkspace.get_main_pathes(view)
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

	def save_to_file(self, project_folder=None):
		project_folder = QspWorkspace.get_cur_pf(project_folder)
		if project_folder is None:
			return None
		qsp_workspace = self.get_json_struct()
		with open(os.path.join(project_folder, 'qsp-project-workspace.json'), "w", encoding="utf-8") as ws_file:
			json.dump(qsp_workspace, ws_file, indent=4)

	def get_locs(self):
		return zip(self.loc_names, self.loc_regions, self.loc_places)

	@staticmethod
	def get_cur_pf(project_folder=None): # -> str or None 
		if not project_folder is None:
			return project_folder
		argv = sublime.active_window().extract_variables()
		return (argv['folder'] if 'folder' in argv else None)

	@staticmethod
	def get_main_pathes(view):
		current_qsps = view.file_name()
		argv = sublime.active_window().extract_variables()
		project_folder = (argv['folder'] if 'folder' in argv else None)
		return current_qsps, project_folder

	@staticmethod
	def get_all_qsplocs(view):
		all_qsplocs = []
		argv = sublime.active_window().extract_variables()
		project_folder = (argv['folder'] if 'folder' in argv else None)
		if project_folder in QSP_WORKSPACES:
			# if ws exist in dict of wss
			qsp_ws = QSP_WORKSPACES[project_folder]
			qsp_ws.refresh_locs_from_symbols(view)
			all_qsplocs = qsp_ws.get_locs()
		else:
			# if ws dont exist in dict of wss
			for s in view.symbols():
				region, name = s
				if name.startswith('Локация: '):
					all_qsplocs.add_loc((name[9:], [region.begin(), region.end()], ''))
		return all_qsplocs

	@staticmethod
	def get_qsplabels_from_symbols(view, exclude_inputting=None): # View, Region -> list
		"""
			Return list of QSP-labels created on this view
		"""
		qsp_labels = []
		for s in view.symbols():
			region, name = s
			if exclude_inputting is None or region != exclude_inputting:
				if name.startswith('Метка: '):
					qsp_labels.append(name[7:])
		return(qsp_labels)

class QspBuildCommand(sublime_plugin.WindowCommand):
	"""
		QSP-Game Builder. Build and run QSP-game from sources. Need a project.json.
	"""
	def run(self, qsp_mode = "--br"):
		# Default paths to converter and player.
		converter = "qsps_to_qsp" # buil-in converter. WARNING! Test-mode!!!
		player = "C:\\Program Files\\QSP\\qsp580\\qspgui.exe"

		# Three commands from arguments.
		argv = self.window.extract_variables()
		args = parse_args([qsp_mode, argv['file']])

		# -----------------------------------------------------------------------
		# args["point_file"] - start point for search `project.json`
		# args["build"] - command for build the project
		# args["run"] - command for run the project
		# -----------------------------------------------------------------------

		# Initialise of Builder:
		builder = BuildQSP(args, converter, player)
		# Run the Builder to work:
		builder.build_and_run()

class QspToQspsCommand(sublime_plugin.WindowCommand):
	""" Command to start converting QSP-file to qsps """
	def run(self):
		argv = self.window.extract_variables()
		file = argv['file']
		if argv['file_extension'] == 'qsp':
			qsp_to_qsps = QspToQsps(args = {'game-file': file})
			qsp_to_qsps.convert()
		else:
			print('Wrong extension of file. Can not convert.')

class QspsToQspCommand(sublime_plugin.WindowCommand):

	def run(self):
		argv = self.window.extract_variables()
		if argv['file_extension'] in ('qsps', 'qsp-txt', 'txt-qsp'):
			file = NewQspsFile(input_file = argv['file'])
			file.convert()
		else:
			print('Wrong extension of file. Can not convert.')

class QspSplitterCommand(sublime_plugin.WindowCommand):

	def run(self):
		argv = self.window.extract_variables()
		if argv['file_extension'] in ('qsps', 'qsp-txt', 'txt-qsp'):
			QspSplitter(args = {'qsps-file': argv['file']}).split_file()
		elif argv['file_extension'] == 'qsp':
			QspSplitter(args = {'game-file': argv['file']}).split_file()
		else:
			print('Wrong extension of file. Can not convert.')

class QspSplitProjectCommand(sublime_plugin.WindowCommand):

	def run(self):
		argv = self.window.extract_variables()
		FinderSplitter(folder_path = argv['file_path'])

class QspNewProjectCommand(sublime_plugin.WindowCommand):

	def run(self):
		argv = self.window.extract_variables()
		if 'folder' in argv:
			jont = os.path.join
			safe_mk_fold(jont(argv['folder'],'[disdocs]'))
			safe_mk_fold(jont(argv['folder'], '[output_game]', 'assets', 'img'))
			safe_mk_fold(jont(argv['folder'], '[output_game]', 'assets', 'snd'))
			safe_mk_fold(jont(argv['folder'], '[output_game]', 'assets', 'vid'))
			safe_mk_fold(jont(argv['folder'], '[output_game]', 'lib'))
			safe_mk_fold(jont(argv['folder'], '[source]'))
			# crete project.json
			project_json_path = jont(argv['folder'], '[source]', 'project.json')
			if not os.path.isfile(project_json_path):
				with open(project_json_path, 'w', encoding='utf-8') as file:
					json.dump(const.QSP_PROJECT_JSON, file, indent=4)
			# create sublime-project
			path, fname = os.path.split(argv['folder'])
			sublproj_path = jont(argv['folder'], fname + '.sublime-project')
			if not os.path.isfile(sublproj_path):
				with open(sublproj_path, 'w', encoding='utf-8') as file:
					file.writelines(const.QSP_SUBLIME_PROJECT)
			# create startfile
			start_file_path = jont(argv['folder'], '[source]', '00_start.qsps')
			if not os.path.isfile(start_file_path):
				with open(start_file_path, 'w', encoding='utf-8') as file:
					file.writelines(const.QSP_START_TEMPLATE)
				self.window.open_file(start_file_path)

class QspNewGameHeadCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		self.view.insert(edit, 0, 'QSP-Game .New qsps-file.\n\n')

class QspNewGameCommand(sublime_plugin.WindowCommand):
	def run(self):
		new_view = self.window.new_file(syntax='Packages/QSP/qsp.sublime-syntax')
		self.window.focus_view(new_view)
		self.window.run_command('qsp_new_game_head')

class QspInvalidInput(sublime_plugin.EventListener):
	def on_modified(self, view):
		if view.syntax() is None or view.syntax().name != 'QSP':
			return None
		begin = view.sel()[0].begin()
		end = view.sel()[0].end()
		sr_locname = view.expand_to_scope(begin, 'meta.start_location.qsp')
		sr_lblname = view.expand_to_scope(begin, 'entity.name.qlabel.qsp')
		if begin == end and sr_locname is not None:
			input_text = view.substr(sr_locname)
			all_locations = QspWorkspace.get_all_qsplocs(view) # list
			loc_names, loc_regions, loc_paths = zip(*all_locations) 
			if not input_text in loc_names:
				return None
			i = loc_names.index(input_text)
			region = sublime.Region(loc_regions[i][0], loc_regions[i][1])
			current_qsps, project_folder = QspWorkspace.get_main_pathes(view)
			if not (current_qsps is None or project_folder is None):
				qsps_relpath = os.path.relpath(current_qsps, project_folder)
			else:
				qsps_relpath = ''
			if sr_locname.intersects(region) and qsps_relpath == loc_paths[i]:
				return None
			content = sublime.expand_variables(const.QSP_WRONG_LOC_MSG, {"input_text": input_text})
			# view.show_popup(content, flags=32+8, location=begin+5, max_width=250)
			sublime.message_dialog(content)
		if begin == end and sr_lblname is not None:
			input_text = view.substr(sr_lblname)
			qsp_labels = QspWorkspace.get_qsplabels_from_symbols(view, exclude_inputting=sr_lblname)
			if input_text in qsp_labels:
				content = sublime.expand_variables(const.QSP_WRONG_LBL_MSG, {"input_text": input_text})
				# view.show_popup(content, flags=sublime.HTML, location=-1, max_width=250)
				sublime.message_dialog(content)

class QspTips(sublime_plugin.EventListener):

	def on_selection_modified(self, view):
		""" Show tips in statusbar """
		if view.syntax() is not None and view.syntax().name == 'QSP':
			word_coords = view.word(view.sel()[0].begin()) # Region
			word = view.substr(word_coords).lower() # str
			p = word_coords.begin()-1 # int (Point)
			pref = (view.substr(word_coords.begin()-1) if p > -1 else '') # str
			keywords = const.QSP_CMD_TIPS.keys()
			if pref == '*' and ('*' + word in keywords):
				word = '*' + word
				match = re.match(r'^\*\w+\b$', word)
			elif pref == '$' and ('$' + word in keywords):
				word = '$' + word
				match = re.match(r'^\$\w+\b$', word)
			else:
				match = re.match(r'^\w+\b$', word)
			if (match is not None) and (word in keywords):
				sublime.status_message(const.QSP_CMD_TIPS[word])

# class QspAddLighting(sublime_plugin.EventListener):

# 	def on_selection_modified(self, view):
# 		""" HighLight- """
# 		global QSP_TRYER
# 		if view.syntax() is not None and view.syntax().name == 'QSP':
# 			if QSP_TRYER:
# 				user_variable = r'\$?[A-Za-zА-Яа-я_][\w\.]*'
# 				regions = view.find_all(user_variable, 2)
# 				variables = set()
# 				for r in regions:
# 					if view.match_selector(r.begin(), 'meta.user-variables.qsp'):
# 						variables.add(view.substr(r))
# 				print(list(variables))
# 				QSP_TRYER = False

class QspAutocomplete(sublime_plugin.EventListener):
	""" Autocomplete and helptips """

	def on_query_completions(self, view, prefix, locations):
		""" append completions in editor """
		if view.syntax() is None or view.syntax().name != 'QSP':
			return []
		# extract all datas
		all_locations = QspWorkspace.get_all_qsplocs(view) # -> list of locations
		# if syntshugarfunc
		if view.match_selector(locations[0]-1, 'variable.function.qsp'):
			qsp_locations = []
			prefix = prefix.lower()
			for loc_name, loc_region, loc_path in all_locations:
				if loc_name.lower().startswith(prefix):
					d = sublime.CompletionItem(
						loc_name,
						annotation="Локация",
						completion=loc_name,
						completion_format=sublime.COMPLETION_FORMAT_TEXT,
						kind=sublime.KIND_FUNCTION
					)
					qsp_locations.append(d)
			return (qsp_locations, 24)
		# if calable operator call location
		elif view.match_selector(locations[0]-1, 'callable_locs.qsp'):
			qsp_locations = []
			scope_region = view.expand_to_scope(locations[0]-1, 'callable_locs.qsp')
			input_text = view.substr(scope_region)
			for loc_name, loc_region, loc_path in all_locations:
				if loc_name.lower().startswith(input_text[1:-1]):
					d = sublime.CompletionItem(
						loc_name,
						annotation="Локация",
						completion=loc_name,
						completion_format=sublime.COMPLETION_FORMAT_TEXT,
						kind=sublime.KIND_FUNCTION
					)
					qsp_locations.append(d)
			return (qsp_locations, 24)
		elif view.match_selector(locations[0]-1, 'label_to_jump.qsp'):
			all_labels = QspWorkspace.get_qsplabels_from_symbols(view)
			scope_region = view.expand_to_scope(locations[0]-1, 'label_to_jump.qsp')
			input_text = view.substr(scope_region)
			qsp_labels = []
			for qsp_lb in all_labels:
				if qsp_lb.lower().startswith(input_text[1:-1]):
					d = sublime.CompletionItem(
						qsp_lb,
						annotation="Метка",
						completion=qsp_lb,
						completion_format=sublime.COMPLETION_FORMAT_TEXT,
						kind=sublime.KIND_MARKUP
					)
					qsp_labels.append(d)
			return (qsp_labels, 24)
		else:
			return []

class QspWorkspaceLoader(sublime_plugin.EventListener):
	""" Manage a qsp-workspace in ram and in files """

	commands_log = {'current': '', 'last': ''}

	def _extract_qsp_ws(self):
		""" extract ws from file if file is exist, and load in ram """
		argv = sublime.active_window().extract_variables()
		project_folder = (argv['folder'] if 'folder' in argv else None)
		if project_folder is None:
			return None
		qws = QSP_WORKSPACES[project_folder] = QspWorkspace()
		if os.path.isfile(os.path.join(project_folder, 'qsp-project-workspace.json')):
			# если файл существует, извлекаем из файла
			qws.extract_from_file(project_folder=project_folder)

	def _save_qsp_ws(self, view):
		""" save ws from ram in file """
		current_qsps = view.file_name()
		if current_qsps is None:
			return None
		argv = sublime.active_window().extract_variables()
		project_folder = (argv['folder'] if 'folder' in argv else None)
		if project_folder is None:
			return None
		if project_folder in QSP_WORKSPACES:
			# if ws exist in dict of wss
			qsp_ws = QSP_WORKSPACES[project_folder]
		else:
			# if ws dont exist in dict of wss
			qsp_ws = QSP_WORKSPACES[project_folder] = QspWorkspace()
		qsp_ws.refresh_locs_from_symbols(view)
		qsp_ws.save_to_file(project_folder)

	def _after_replace(self, command_name:str = ''):
		print('commands_log', self.commands_log)
		self.commands_log['last'], self.commands_log['current'] = self.commands_log['current'], command_name
		if self.commands_log['last'] in ('delete_file', 'rename_path'):
			project_folder = QspWorkspace.get_cur_pf()
			if project_folder is None or not project_folder in QSP_WORKSPACES:
				return None
			qsp_ws = QSP_WORKSPACES[project_folder]
			sublime.set_timeout_async(lambda: qsp_ws.refresh_files_paths(), 180)

	def on_close(self, view):
		if view.syntax() is not None and view.syntax().name == 'QSP':
			self._save_qsp_ws(view)

	def on_pre_save(self, view):
		if view.syntax() is not None and view.syntax().name == 'QSP':
			self._save_qsp_ws(view)

	def on_init(self, views):
		self._extract_qsp_ws()

	def on_load_project(self, window:sublime.Window) -> None:
		self._extract_qsp_ws()

# variables
QSP_WORKSPACES = {} # all qsp workspaces add to this dict, if you open project
QSP_TRYER = True
QSP_TEMP = {}
