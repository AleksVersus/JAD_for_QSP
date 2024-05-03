import os 
import subprocess
import json

# Importing my modules.
from . import function as qsp
from .qsps_to_qsp import ModuleQSP
import time


class BuildQSP():
	"""
		Procedure of building is need of global name-space, but it is wrong.
		If we make the class ex, we can use class instance fields as global name-space.
		Class BuildQSP — is a name-space for procedure scripts.
	"""
	def __init__(self, args:dict) -> None:
		# Init main fields:
		self.args = args 											# Arguments from sys.
		self.converter = 'qsps_to_qsp'								# Converter application path (exe in win).
		self.converter_param = ''
		self.player = 'C:\\Program Files\\QSP\\qsp580\\qspgui.exe'	# Player application path (exe in win)

		# Default inits.
		self.root = {}
		self.save_txt2gam = False
		self.include_scripts = []
		self.prove_file_loc = None
		self.export_files_paths = []
		self.start_file = '' # File, that start in player.
		self.work_dir = None

		# Init work dir.
		self.work_dir_init()
		
		if self.work_dir is not None:
			# Reinit main fields and init other fields.
			self.fields_init()
			# Init start-file.
			self.start_file_init()

	def work_dir_init(self) -> None:
		point_file = self.args['point_file']
		project_folder = qsp.search_project_folder(point_file)

		if qsp.need_project_file(project_folder, point_file, self.player):
			# If project-file's folder is not found, but other
			# conditional is right, generate the new project-file.
			project_folder = os.path.split(point_file)[0]
			project_dict = qsp.get_point_project(point_file, self.player)
			project_json = json.dumps(project_dict, indent=4)
			project_file_path = os.path.join(project_folder, 'qsp-project.json')

			with open(project_file_path, 'w', encoding='utf-8') as file:
				file.write(project_json)
				
			qsp.write_error_log(f'[100] File «{project_file_path}» was created.')

		self.set_work_dir(project_folder)

	def set_work_dir(self, work_dir:str=None) -> None:
		self.work_dir = work_dir
		# Change work dir:
		if self.work_dir is not None:
			os.chdir(self.work_dir)

	def fields_init(self) -> None:	
		# Deserializing project-file:
		project_json = os.path.join(self.work_dir, 'qsp-project.json')
		with open(project_json, 'r', encoding='utf-8') as project_file:
			self.root = json.load(project_file)

		# Get paths to converter and player (not Deafault)
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
		if ('save_txt2gam' in self.root) and (self.root['save_txt2gam'] == 'True'):
			self.save_txt2gam = True
		else:
			self.save_txt2gam = False

		# Postprocessor's scripts list (or none):
		if 'postprocessors' in self.root:
			self.include_scripts = self.root['postprocessors']
		else:
			self.include_scripts = None

		# Preprocessor's mode init.
		if not 'preprocessor' in self.root:
			self.root['preprocessor'] = 'Off'

		# Location's of scaned files name init.
		if ('scans' in self.root) and ('start' in self.root):
			if 'destination' in self.root['scans']:
				self.prove_file_loc = self.root['scans']['destination']
			else:
				self.prove_file_loc = None

	def start_file_init(self):
		if self.work_dir is None:
			qsp.write_error_log('[101] Builder design error. Work dir is not init.')
			return None
		if 'start' in self.root:
			# Start-file defined. Get from define.
			self.start_file = os.path.abspath(self.root['start'])

	def get_start_file(self) -> None:
		if self.need_build_file():
			# Start-file is not defined, but list of build-files is exist.
			self.start_file = self.export_files_paths[0]
			qsp.write_error_log(f'[102] Start-file is wrong. Used «{self.start_file}» for run.')
		if self.need_point_file():
			# Start-file is not defined, list of build-files is not exist, but run point_file.
			self.start_file = self.args['point_file']
		return self.start_file
			
	def build_and_run(self):
		# Print builder's mode.
		qsp.print_builder_mode(self.args['build'], self.args['run'])

		if self.args['build']:
			if self.prove_file_loc is not None:
				# Generate location with files-list.
				self.create_scans_loc()
			# Build QSP-files.
			self.build_qsp_files()

		if self.args['run']:
			# Run Start QSP-file.
			self.run_qsp_files()

	def create_scans_loc(self):
		# FoolProof.
		if not (('scans' in self.root) and ('start' in self.root)):
			qsp.write_error_log('[103] Builder design error. Prove file locations is not defined.')
			return

		found_files = [] # Absolute files paths.
		start_file_folder = os.path.split(self.start_file)[0]
		scans = self.root['scans']
		func_name = (scans['location'] if 'location' in scans else 'prv_file')

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
			'QSP-Game Функция для проверки наличия файлов.\n',
			f'# {func_name}\n',
			'$args[0]=$args[0] & !@ путь к файлу, который нужно проверить\n',
			'$args[1]="\n']

		for file in found_files:
			sf, f = qsp.compare_paths(start_file_folder, os.path.abspath(file))
			qsp_file_body.append('['+f+']\n')

		qsp_file_body.extend([
			'"\n',
			'result = iif(instr($args[1],"[<<$args[0]>>]")<>0, 1, 0)\n',
			f'- {func_name}\n'])

		# create folder if it's not exist
		qsp.safe_mk_fold(self.prove_file_loc)
		# Create file next to project-file:
		of = os.path.join(self.prove_file_loc, 'prove_file_func.qsps_')
		with open(of, 'w',encoding='utf-8') as file:
			file.writelines(qsp_file_body)
		self.prove_file_loc = of
		# Add file-path to build:
		# if 'files' in self.root['project'][0]:
		# 	self.root['project'][0]['files'].append({'path':'.\\prvFile_location.qspst'})
		# else:
		# 	self.root['project'][0]['files'] = [{'path':'.\\prvFile_location.qspst'}]		

	def build_qsp_files(self):
		start_time = time.time()
		pp_markers = {'Initial':True, 'True':True, 'False':False} # Preproc markers, variables.
		project = self.root['project']
		# Get instructions list from 'project'.
		for instruction in project:
			qsp_module = ModuleQSP()
			qsp_module.set_converter(self.converter, self.converter_param)
			if 'files' in instruction:
				qsp_module.extend_by_files(instruction['files'])
			if 'folders' in instruction:
				for path in instruction['folders']:
					qsp_module.extend_by_folder(os.path.abspath(path['path']))
			if (not 'files' in instruction) and (not 'folders' in instruction):
				qsp_module.extend_by_folder(os.getcwd())
			if not self.prove_file_loc is None:
				qsp_module.extend_by_files([{'path': self.prove_file_loc}])
				self.prove_file_loc = None
			# print(f'extended files: {start_time - time.time()}')
			if 'build' in instruction:
				qsp_module.exit_files(instruction['build'])
			else:
				qsp_module.exit_files(f'game{project.index(instruction)}.qsp')
				qsp.write_error_log(f'[106] Key «build» not found. Choose export name {qsp_module.output_qsp}.')

			if 'postprocessor' in instruction:
				# Include scripts in build instructions have priority.
				qsp_module.extend_scripts(instruction['postprocessors'])
			elif self.include_scripts is not None:
				qsp_module.extend_scripts(self.include_scripts)

			# Build TXT2GAM-file
			# qsp.construct_file(build_files, exit_txt, self.root['preprocessor'], pp_markers, code_system=code_system)
			qsp_module.preprocess_qsps(self.root['preprocessor'], pp_markers)
			# print(f'preprocess: {start_time - time.time()}')
			qsp_module.extract_qsps()
			# print(f'extracting qsps: {start_time - time.time()}')
			# Run Postprocessor if include scripts are exists.
			qsp_module.postprocess_qsps()
			print(f'postprocess: {time.time() - start_time}')
			# Convert TXT2GAM at `.qsp`
			qsp_module.convert(self.save_txt2gam)
			print(f'convert: {time.time() - start_time}')
			if os.path.isfile(qsp_module.output_qsp):
				self.export_files_paths.append(qsp_module.output_qsp)			

	def run_qsp_files(self):
		start_file = self.get_start_file()

		if not os.path.isfile(self.player):
			qsp.write_error_log(f'[107] Path at player is wrong. Prove path «{self.player}».')
			return None
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

	def need_point_file(self):
		"""
			Unloading conditions.
			If not `start` in root or not exist start-file, 
			and running file is qsp, return True, other False.
		"""
		cond = all((
			(not 'start' in self.root) or (not os.path.isfile(self.start_file)),
			os.path.splitext(self.args['point_file'])[1] == '.qsp'))
		return (True if cond else False)

	def need_build_file(self):
		cond = all((
			(not 'start' in self.root) or (not os.path.isfile(self.start_file)),
			len(self.export_files_paths) > 0))
		return (True if cond else False)

