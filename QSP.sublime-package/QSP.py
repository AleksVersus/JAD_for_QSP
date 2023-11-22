import sublime
import sublime_plugin

import sys, os

# Importing my modules from qSpy package.
from .qSpy.function import parse_args
from .qSpy.builder import BuildQSP
from .qSpy.qsp_to_qsps import QspToQsps
from .qSpy.qsps_to_qsp import NewQspsFile
from .qSpy.qsp_splitter import QspSplitter
from .qSpy.main_cs import FinderSplitter

def safe_mk_fold(new_path):
	if not os.path.isdir(new_path):
		os.mkdir(new_path)

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
			safe_mk_fold(argv['folder'] + '\\[disdocs]')
			safe_mk_fold(argv['folder'] + '\\[output_game]')
			safe_mk_fold(argv['folder'] + '\\[output_game]\\assets')
			safe_mk_fold(argv['folder'] + '\\[output_game]\\assets\\img')
			safe_mk_fold(argv['folder'] + '\\[output_game]\\assets\\snd')
			safe_mk_fold(argv['folder'] + '\\[output_game]\\assets\\vid')
			safe_mk_fold(argv['folder'] + '\\[output_game]\\lib')
			safe_mk_fold(argv['folder'] + '\\[source]')
			# crete project.json
			if not os.path.isfile(argv['folder']+'\\project.json'):
				project_json = [
					'{\n\t"project":\n\t[\n\t\t{\n\t\t\t"build":".\\\\[output_game]\\\\game_start.qsp"',
					',\n\t\t\t"folders":\n\t\t\t[\n\t\t\t\t{"path":".\\\\[source]"}\n\t\t\t]\n\t\t}',
					'\n\t],\n\t"start":".\\\\[output_game]\\\\game_start.qsp"',
					',\n\t"player":"C:\\\\Program Files\\\\QSP\\\\qsp580\\\\qspgui.exe"\n}'
				]
				with open(argv['folder']+'\\project.json', 'w', encoding='utf-8') as file:
					file.writelines(project_json)
			# create sublime-project
			path, fname = os.path.split(argv['folder'])
			if not os.path.isfile(argv['folder']+'\\'+fname+'.sublime-project'):
				sublime_project = [
					'{\n\t"folders":\n\t[\n\t\t{\n\t\t\t"path": ".",\n\t\t}\n\t]\n}'
				]
				with open(argv['folder']+'\\'+fname+'.sublime-project', 'w', encoding='utf-8') as file:
					file.writelines(sublime_project)
			# create startfile
			if not os.path.isfile(argv['folder']+'\\[source]\\00_start.qsps'):
				start_file = [
					'QSP-Game Start game from this location\n\n',
					'# [start]\n',
					'*pl "Quick project start location. Edit this file, and appending new."\n',
					'*pl "Стартовая локация быстрого проекта. ',
					'Отредактируйте этот файл и добавьте новые."\n',
					'--- [start] ---\n'
				]
				with open(argv['folder']+'\\[source]\\00_start.qsps', 'w', encoding='utf-8') as file:
					file.writelines(start_file)
				self.window.open_file(argv['folder']+'\\[source]\\00_start.qsps')