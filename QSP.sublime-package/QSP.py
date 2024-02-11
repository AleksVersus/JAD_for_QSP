import sublime
import sublime_plugin

import os
import re
import json

# Importing my modules from qSpy package.
from .qSpy.pad import QSpyFuncs as qspf
from .qSpy.builder import BuildQSP
from .qSpy.qsp_to_qsps import QspToQsps
from .qSpy.qsps_to_qsp import NewQspsFile
from .qSpy.qsp_splitter import QspSplitter
from .qSpy.main_cs import FinderSplitter
from .qSpy.workspace import QspWorkspace
# Import constants
from .qSpy import const


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
		args = qspf.parse_args([qsp_mode, argv['file']])

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
	""" Command to start converting QSP-Game to qsps """
	def run(self):
		argv = self.window.extract_variables()
		file = argv['file']
		if argv['file_extension'] == 'qsp':
			qsp_to_qsps = QspToQsps(args = {'game-file': file})
			qsp_to_qsps.convert()
		else:
			print('Wrong extension of file. Can not convert.')

class QspsToQspCommand(sublime_plugin.WindowCommand):
	""" Comand to start converting qsps-file to QSP-Game """
	def run(self):
		argv = self.window.extract_variables()
		if argv['file_extension'] in ('qsps', 'qsp-txt', 'txt-qsp'):
			file = NewQspsFile(input_file = argv['file'])
			file.convert()
		else:
			print('Wrong extension of file. Can not convert.')

class QspSplitterCommand(sublime_plugin.WindowCommand):
	"""
		Start command of split QSP-Game or qsps-file
		at some qsps-files.
	"""
	def run(self):
		argv = self.window.extract_variables()
		if argv['file_extension'] in ('qsps', 'qsp-txt', 'txt-qsp'):
			QspSplitter(args = {'qsps-file': argv['file']}).split_file()
		elif argv['file_extension'] == 'qsp':
			QspSplitter(args = {'game-file': argv['file']}).split_file()
		else:
			print('Wrong extension of file. Can not convert.')

class QspSplitProjectCommand(sublime_plugin.WindowCommand):
	""" Start command of convert and split QSP-pproject """
	def run(self):
		argv = self.window.extract_variables()
		FinderSplitter(folder_path = argv['file_path'])

class QspNewProjectCommand(sublime_plugin.WindowCommand):
	""" Create New Standart QSP-project """
	def run(self):
		argv = self.window.extract_variables()
		if not 'folder' in argv: return None
		jont = os.path.join
		qspf.safe_mk_fold(jont(argv['folder'],'[disdocs]'))
		qspf.safe_mk_fold(jont(argv['folder'], '[output_game]', 'assets', 'img'))
		qspf.safe_mk_fold(jont(argv['folder'], '[output_game]', 'assets', 'snd'))
		qspf.safe_mk_fold(jont(argv['folder'], '[output_game]', 'assets', 'vid'))
		qspf.safe_mk_fold(jont(argv['folder'], '[output_game]', 'lib'))
		qspf.safe_mk_fold(jont(argv['folder'], '[source]'))
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
	""" Generate New game Head and insert in viewport """
	def run(self, edit):
		qsps_text = ''.join(const.QSP_START_TEMPLATE)
		self.view.insert(edit, 0, qsps_text)

class QspNewGameCommand(sublime_plugin.WindowCommand):
	""" Generate new viewport with QSP-syntax """
	def run(self):
		new_view = self.window.new_file(syntax='Packages/QSP/qsp.sublime-syntax')
		self.window.focus_view(new_view)
		self.window.run_command('qsp_new_game_head')

class QspInvalidInput(sublime_plugin.EventListener):
	"""
		Wrong input of qsp-locs names or labels names
	"""

	def on_modified(self, view):
		if view.syntax() is None or view.syntax().name != 'QSP':
			return None
		begin = view.sel()[0].begin()
		end = view.sel()[0].end()
		sr_locname = view.expand_to_scope(begin, 'meta.start_location.qsp')
		sr_lblname = view.expand_to_scope(begin, 'entity.name.qlabel.qsp')
		if begin == end and sr_locname is not None:
			input_region = [sr_locname.begin(), sr_locname.end()]
			input_text = view.substr(sr_locname)
			current_qsps, project_folder = QspWorkspace.get_main_pathes(view)
			if not any((
				current_qsps is None,
				project_folder is None,
				os.path.commonprefix([current_qsps, project_folder]) == '')):
				qsps_relpath = os.path.relpath(current_qsps, project_folder)
			else:
				qsps_relpath = ''
			_filting_qsplocs = lambda qsp_loc: not qsp_loc[1] == input_region and qsp_loc[2] == qsps_relpath
			all_locations = list(filter(_filting_qsplocs, QspWorkspace.get_all_qsplocs(view, QSP_WORKSPACES)))
			loc_names, _, _ = zip(*all_locations)
			if not input_text in loc_names:
				return None
			content = sublime.expand_variables(const.QSP_MSG.WRONG_LOC, {"input_text": input_text})
			# view.show_popup(content, flags=32+8, location=begin+5, max_width=250)
			sublime.message_dialog(content)
		if begin == end and sr_lblname is not None:
			input_text = view.substr(sr_lblname)
			qsp_labels = QspWorkspace.get_qsplbls(view, exclude_inputting=sr_lblname)
			if input_text in qsp_labels:
				content = sublime.expand_variables(const.QSP_MSG.WRONG_LBL, {"input_text": input_text})
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
		all_locations = QspWorkspace.get_all_qsplocs(view, QSP_WORKSPACES) # -> list of locations
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
			all_labels = QspWorkspace.get_qsplbls(view)
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
		qws = QSP_WORKSPACES[project_folder] = QspWorkspace(QSP_WORKSPACES)
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
			qsp_ws = QSP_WORKSPACES[project_folder] = QspWorkspace(QSP_WORKSPACES)
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
