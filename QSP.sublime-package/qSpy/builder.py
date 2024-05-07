import os 
import subprocess
import json

# Importing my modules.
from . import function as qsp
from .moduleqsp import ModuleQSP
import time


class BuildQSP():
	"""
		Procedure of building is need of global name-space, but it is wrong.
		If we make the class ex, we can use class instance fields as global name-space.
		Class BuildQSP — is a name-space for procedure scripts.
	"""
	def __init__(self, modes:dict) -> None:
		# Init main fields:
		self.modes = modes 											# Arguments from sys. Modes of build.
		self.converter = 'qsps_to_qsp'								# Converter application path (exe in win).
		self.converter_param = ''									# Converter's parameters (key etc.)
		self.player = 'C:\\Program Files\\QSP\\qsp580\\qspgui.exe'	# Player application path (exe in win)

		# Default inits.
		self.root = {}					# qsp-project.json
		self.save_temp_files = False	# save temporary qsps-files or not
		self.modules_paths = []			# Output files' paths (QSP-files, modules)
		self.start_module_path = ''		# File, that start in player.
		self.work_dir = None			# workdir - is dir of qsp-project.json

		# Scanned files proves location
		self.scan_the_files = False		# Marker of scanning files
		self.scan_files_locname = None	# location name
		self.scan_files_locbody = []	# location body
		self.SCANFILES_LOCNAME = 'prv_file' # constanta of standart locname

		# Init work dir.
		self.work_dir_init()
		
		if self.work_dir is not None:
			# Reinit main fields and init other fields.
			self.fields_init()

	def work_dir_init(self) -> None:
		"""
			Initialise of workdir. If qsp-project.json is not exist,
			workdir sets at dir of point file.
		"""
		point_file = self.modes['point_file']
		project_folder = qsp.search_project_folder(point_file)

		if self.project_file_is_need(project_folder, point_file, self.player):
			# If project_folder is not found, but other
			# conditional is right, generate the new project-file.
			project_folder = os.path.split(point_file)[0]
			self.create_point_project(project_folder, point_file)

		self.set_work_dir(project_folder)

	def set_work_dir(self, work_dir:str=None) -> None:
		""" Set self.work_dir and change work dir """
		self.work_dir = work_dir
		# Change work dir:
		if self.work_dir is not None:
			os.chdir(self.work_dir)

	def fields_init(self) -> None:
		""" Filling the BuildQSP fields from project_file """
		if not self.root: # self.root is empty
			# Deserializing project-file:
			project_json = os.path.join(self.work_dir, 'qsp-project.json')
			with open(project_json, 'r', encoding='utf-8') as project_file:
				self.root = json.load(project_file)

		# Get paths to converter and player (not Default)
		if 'converter' in self.root:
			converter = self.root['converter']
			_is_file = lambda path: os.path.isfile(os.path.abspath(path))
			if type(converter) == str and _is_file(converter):
				self.converter = os.path.abspath(converter)
				self.converter_param = ''
			elif type(converter) == list and len(converter)>1 and _is_file(converter[0]):
				self.converter  = os.path.abspath(converter[0])
				self.converter_param = converter[1]
			elif type(converter) == list and _is_file(converter[0]):
				self.converter  = os.path.abspath(converter[0])
				self.converter_param = ''

		if 'player' in self.root:
			if os.path.isfile(os.path.abspath(self.root['player'])):
				self.player = os.path.abspath(self.root['player'])

		# Save temp-files Mode:
		if ('save_temp_files' in self.root):
			self.save_temp_files = self.root['save_temp_files']

		# Preprocessor's mode init.
		if not 'preprocessor' in self.root:
			self.root['preprocessor'] = 'Off'

		# Location's of scaned files name init.
		if ('scans' in self.root) and ('start' in self.root):
			# mode is switchon, if folders or files adding
			if 'folders'in self.root['scans'] or 'files' in self.root['scans']:
				self.scan_the_files = True
			# choose name of location
			if 'location' in self.root['scans']:
				self.scan_files_locname = self.root['scans']['location']
			else:
				self.scan_files_locname = self.SCANFILES_LOCNAME
			# if 'destination' in self.root['scans']:
			# 	self.scanned_files_qsps = self.root['scans']['destination']
			# else:
			# 	self.scanned_files_qsps = None

		if 'start' in self.root:
			# Start-file defined. Get from define.
			self.start_module_path = os.path.abspath(self.root['start'])

	def build_and_run(self):
		self.print_mode()

		if self.modes['build']:
			if self.scan_the_files:
				# Generate location with files-list.
				self.create_scans_loc()
			# Build QSP-files.
			self.build_qsp_files()

		if self.modes['run']:
			# Run Start QSP-file.
			self.run_qsp_files()

	def get_start_module(self) -> str:
		""" Get file what run in player after building """
		if self.need_build_file():
			# Start-file is not defined, but list of module-files is exist.
			self.start_module_path = self.modules_paths[0]
			qsp.write_error_log(f'[102] Start-file is wrong. Used «{self.start_module_path}» for run.')
		if self.need_point_file():
			# Start-file is not defined, list of build-files is not exist, but run point_file.
			self.start_module_path = self.modes['point_file']
		return self.start_module_path
			
	
	def create_scans_loc(self) -> None:
		""" Prepare and creation location-function of scanned files """
		found_files = [] # Absolute files paths.
		start_file_folder = os.path.split(self.start_module_path)[0]
		scans = self.root['scans']
		func_name = self.scan_files_locname

		if 'folders' in scans:
			for folder in scans['folders']:
				# Iterate through the folders, comparing the paths with start_file,
				# to understand if the folder lies deeper relative to it.
				sf, f = qsp.compare_paths(start_file_folder, os.path.abspath(folder))
				# print(f'sff:{start_file_folder}, f:{folder}, sf:{sf}, fl:{f}')
				if sf == '.' or sf == '':
					# Folder relative to path.
					found_files.extend(qsp.get_files_list(folder, filters=[]))
				else:
					# Folder is not relative to path. Is error.
					qsp.write_error_log(f'[104] Folder «{folder}» is not in the project.')

		if 'files' in scans:
			for file in scans['files']:
				sf, f = qsp.compare_paths(start_file_folder,os.path.abspath(file))
				if sf == '':
					found_files.append(os.path.abspath(file))
				else:
					qsp.write_error_log(f'[105] File «{file}» is not in the project.')

		qsp_file_body = [
			f'# {func_name}\n',
			'$args[0] = $args[0]\n',
			'$args[1] = "\n']

		for file in found_files:
			sf, f = qsp.compare_paths(start_file_folder, os.path.abspath(file))
			qsp_file_body.append(f'[{f}]\n')

		qsp_file_body.extend([
			'"\n',
			'result = iif(instr($args[1],"[<<$args[0]>>]")<>0, 1, 0)\n',
			f'- {func_name}\n'])

		self.scan_files_locbody = qsp_file_body	

	def build_qsp_files(self):
		start_time = time.time()
		pp_markers = {'Initial':True, 'True':True, 'False':False} # Preproc markers, variables.
		project = self.root['project']
		# Get instructions list from 'project'.
		for instruction in project:
			qsp_module = ModuleQSP()
			qsp_module.set_converter(self.converter, self.converter_param)
			if 'files' in instruction:
				for file in instruction['files']:
					qsp_module.extend_by_file(os.path.abspath(file['path']))
			if 'folders' in instruction:
				for path in instruction['folders']:
					qsp_module.extend_by_folder(os.path.abspath(path['path']))
			if ('files' not in instruction) and ('folders' not in instruction):
				qsp_module.extend_by_folder(self.work_dir) # if not pathes, scan all current folder
			if self.scan_the_files:
				qsp_module.extend_by_src(self.scan_files_locbody)
				self.scan_the_files = False
			# print(f'extended files: {start_time - time.time()}')
			if 'module' in instruction:
				qsp_module.set_exit_files(instruction['module'])
			else:
				qsp_module.exit_files(f'game{project.index(instruction)}.qsp')
				qsp.write_error_log(f'[106] Key «build» not found. Choose export name {qsp_module.output_qsp}.')

			# Build TXT2GAM-file
			# preprocessor work if not Hard-off mode
			if self.root['preprocessor'] != 'Hard-off':
				qsp_module.preprocess_qsps(self.root['preprocessor'], pp_markers)
			# print(f'preprocess: {start_time - time.time()}')
			qsp_module.extract_qsps()
			# print(f'extracting qsps: {start_time - time.time()}')
			# Convert TXT2GAM at `.qsp`
			qsp_module.convert(self.save_temp_files)
			print(f'convert: {time.time() - start_time}')
			if os.path.isfile(qsp_module.output_qsp):
				self.modules_paths.append(qsp_module.output_qsp)			

	def run_qsp_files(self) -> None:
		if not os.path.isfile(self.player):
			qsp.write_error_log(f'[107] Path at player is wrong. Prove path «{self.player}».')
			return None
		
		start_file = self.get_start_module()

		if not os.path.isfile(start_file):
			qsp.write_error_log(f'[108] Start-file is wrong. Don\'t start the player.')
		else:
			proc = subprocess.Popen([self.player, start_file])
			# This instruction kill the builder after 100 ms.
			# It necessary to close process in console window,
			# but player must be open above console.
			try:
				proc.wait(0.1)
			except subprocess.TimeoutExpired:
				pass

	def need_point_file(self) -> bool:
		"""
			Return True if:
			- start-file not defined
			- point file is '.qsp'
		"""
		return all((
			(not 'start' in self.root) or (not os.path.isfile(self.start_module_path)),
			os.path.splitext(self.modes['point_file'])[1] == '.qsp'))

	def need_build_file(self) -> bool:
		""" 
			Return True if:
			- start-file is not define
			- modules path's list not empty
		"""
		return all((
			(not 'start' in self.root) or (not os.path.isfile(self.start_module_path)),
			self.modules_paths))
	
	def create_point_project(self, project_folder:str, point_file:str) -> None:
		project_dict = self.get_point_project(point_file, self.player)
		project_json = json.dumps(project_dict, indent=4)
		project_file_path = os.path.join(project_folder, 'qsp-project.json')

		self.root = project_dict
		with open(project_file_path, 'w', encoding='utf-8') as file:
			file.write(project_json)
			
		qsp.write_error_log(f'[100] File «{project_file_path}» was created.')

	def print_mode(self) -> None:
		""" Print builder's work mode. """
		if self.modes['build'] and self.modes['run']:
			print("Build and Run Mode")
		elif self.modes['build']:
			print("Build Mode")
		elif self.modes['run']:
			print("Run Mode")

	@staticmethod
	def project_file_is_need(project_folder:str, point_file:str, player_path:str) -> bool:
		"""
			Return True if:
			- project-file not found,
			- point file is '.qsps', 
			- player-path is right.
		"""
		return all((
			project_folder is None,
			os.path.splitext(point_file)[1] == '.qsps',
			os.path.isfile(player_path)))

	@staticmethod
	def get_point_project(point_file:str, player:str) -> dict:
		"""	Create standart structure of project-file for start from point_file. """
		game_name = os.path.splitext(os.path.split(point_file)[1])[0]+'.qsp'
		project_dict = {
			"project":
			[
				{
					"build": game_name,
					"files":
					[
						{"path": point_file}
					]
				}
			],
			"start": game_name,
			"player": player
		}
		return project_dict

