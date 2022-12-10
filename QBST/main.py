# QSP-builder

# Sorry My BAD English!!!

# Build the game-files in ".qsp"-format from text-files in TXT2GAM-format.
# Собирает файлы игр формата ".qsp" из текстовых файлов формата TXT2GAM.

# Don't use this script as module! Не используйте этот скрипт, как модуль!

# Importing standart modules.
import sys
import os 
import subprocess
import json
import re

# Importing my modules.
import function as qsp
import pp

class BuildQSP():
	"""
		Procedure of building is need of global name-space, but it is wrong.
		If we make the class ex, we can use class instance fields as global name-space.
		Class BuildQSP — is a name-space for procedure scripts.
	"""
	def __init__(self, args, converter, player):
		# Init main fields:
		self.args = args 			# Arguments from sys.
		self.converter = converter	# Converter application path (exe in win).
		self.player = player		# Player application path (exe in win)

		# Default inits.
		self.set_work_dir(None)
		self.root = {}
		self.save_txt2gam = False
		self.include_scripts = []
		self.prove_file_loc = None
		self.export_files_paths = []
		self.start_file = "" # File, that start in player.

		# Init work dir.
		self.work_dir_init()
		# Reinit main fields and init other fields.
		if self.work_dir is not None:
			self.fields_init()
			# Init start-file
			self.start_file_init()

	def work_dir_init(self):
		
		# Path to point file.
		point_file = self.args["point_file"]
		# Search the project-file's folder.
		self.set_work_dir(qsp.search_project_folder(point_file))

		if qsp.need_project_file(self.work_dir, point_file, self.converter, self.player):
			# If project-file's folder is not found, but other
			# conditional is right, generate the new project-file.
			self.set_work_dir(os.path.abspath('.'))

			project_json = qsp.get_standart_project(point_file, self.converter, self.player)
			project_json = project_json.replace('\\', '\\\\')

			with open(self.work_dir+"\\project.json", "w", encoding="utf-8") as file:
				file.write(project_json)
			qsp.write_error_log("error.log", f"[100] File '{work_dir}\\project.json' was created.\n")

	def set_work_dir(self, work_dir):
		self.work_dir = work_dir
		# Change work dir:
		if self.work_dir is not None:
			os.chdir(self.work_dir)

	def fields_init(self):
		if self.work_dir is not None:
			os.chdir(self.work_dir)
			# Deserializing project-file:
			with open("project.json","r",encoding="utf-8") as project_file:
				self.root = json.load(project_file)

			# Get paths to converter and player (not Deafault)
			if "converter" in self.root:
				if os.path.isfile(os.path.abspath(self.root["converter"])):
					self.converter = os.path.abspath(self.root["converter"])
			if "player" in self.root:
				if os.path.isfile(os.path.abspath(self.root["player"])):
					self.player = os.path.abspath(self.root["player"])

			# Save temp-files Mode:
			if "save_txt2gam" in self.root:
				if self.root["save_txt2gam"] == "True":
					self.save_txt2gam = True
				else:
					self.save_txt2gam = False
			else:
				self.save_txt2gam = False

			# Postprocessor's scripts list (or none):
			if "postprocessors" in self.root:
				self.include_scripts = self.root["postprocessors"]
			else:
				self.include_scripts = None

			# Preprocessor's mode init.
			if not "preprocessor" in self.root:
				self.root["preprocessor"]="Off"

			# Location's of scaned files name init.
			if ("scans" in self.root) and ("start" in self.root):
				if "location" in self.root["scans"]:
					self.prove_file_loc=self.root["scans"]["location"]
				else:
					self.prove_file_loc="prvFile"
		else:
			qsp.write_error_log("error.log", f"[102] Builder design error. Work dir is not init.\n")

	def start_file_init(self):
		if self.work_dir is not None:
			os.chdir(self.work_dir)
			if "start" in self.root:
				# Start-file defined. Get from define.
				self.start_file=os.path.abspath(self.root["start"])
			if ((not "start" in self.root) or (not os.path.isfile(self.start_file))) and len(self.export_files_paths)>0:
				# Start-file is not defined, but list of build-files is exist.
				self.start_file=self.export_files_paths[0]
				qsp.write_error_log("error.log", f"[104] main: Start-file is wrong. Used '{self.start_file}' for start the player.\n")
			if qsp.need_point_file(self.root, self.start_file, self.args["point_file"]):
				# Start-file is not defined, list of build-files is not exist, but run point_file.
				self.start_file=self.args["point_file"]
		else:
			qsp.write_error_log("error.log", f"[103] Builder design error. Work dir is not init.\n")

	def build_and_run(self):
		# Print builder's mode.
		qsp.print_builder_mode(self.args["build"], self.args["run"])

		if self.prove_file_loc is not None:
			# Generate location with files-list.
			self.create_scans_loc()

		if self.args["build"]:
			# Build QSP-files.
			self.build_qsp_files()

		if self.args["run"]:
			# Run Start QSP-file.
			self.run_qsp_files()

	def create_scans_loc(self):
		# FoolProof.
		if ("scans" in self.root) and ("start" in self.root):

			found_files = [] # Absolute files paths.
			start_file_folder = os.path.split(self.start_file)[0]

			if "folders" in self.root["scans"]:
				for folder in self.root["scans"]["folders"]:
					# Iterate through the folders, comparing the paths with start_file,
					# to understand if the folder lies deeper relative to it.
					sf, f = qsp.compare_paths(start_file_folder, os.path.abspath(folder))
					if sf == '':
						# Folder relative to path.
						found_files.extend(qsp.get_files_list(folder, filters=[]))
					else:
						# Folder is not relative to path. Is error.
						qsp.write_error_log("error.log", f"[106] Folder '{folder}' is not in the project.\n")

			if "files" in self.root["scans"]:
				for file in self.root["scans"]["files"]:
					sf, f = qsp.compare_paths(start_file_folder,os.path.abspath(file))
					if sf == '':
						found_files.append(os.path.abspath(file))
					else:
						qsp.write_error_log("error.log", f"[107] File '{file}' is not in the project.\n")

			qsp_file_body = [
				'QSP-Game Функция для проверки наличия файлов.\n',
				f'# {self.prove_file_loc}\n',
				'$args[0]=$args[0] & !@ путь к файлу, который нужно проверить\n',
				'$args[1]="\n'
			]

			for file in found_files:
				sf, f = qsp.compare_paths(start_file_folder, os.path.abspath(file))
				qsp_file_body.append(f'[{f}]\n')

			qsp_file_body.extend([
				'"\n',
				'if instr($args[1],"[<<$args[0]>>]")<>0: result=1 else result=0\n',
				f'--- {self.prove_file_loc} ---\n'
			])

			# Create file next to project-file:
			with open('.\\prvFile_location.qspst', 'w',encoding='utf-8') as file:
				file.writelines(qsp_file_body)
			# Add file-path to build:
			if "files" in self.root["project"][0]:
				self.root["project"][0]["files"].append({"path":".\\prvFile_location.qspst"})
			else:
				self.root["project"][0]["files"] = [{"path":".\\prvFile_location.qspst"}]

		else:
			qsp.write_error_log("error.log", f"[105] Builder design error. Prove file locations is not defined.\n")

	def build_qsp_files(self):
		pp_markers={"Initial":True,"True":True,"False":False} # Preproc markers.
		# Get instructions list from "project".
		for instruction in self.root["project"]:
			build_files=[] # Files path for build.
			if "files" in instruction:
				build_files.extend(qsp.gen_files_paths(instruction["files"]))
			if "folders" in instruction:
				for path in instruction["folders"]:
					build_files.extend(qsp.get_files_list(os.path.abspath(path["path"])))
			if (not "files" in instruction) and (not "folders" in instruction):
				build_files.extend(qsp.get_files_list(os.getcwd()))
			# if "top_location" in instruction:
				# Instruction is not supported.
				# pass
			if "build" in instruction:
				exit_qsp, exit_txt = qsp.exit_files(instruction["build"])
			else:
				exit_qsp, exit_txt = qsp.exit_files(f'game{self.root["project"].index(instruction)}.qsp')
				qsp.write_error_log("error.log", f"[108] Key 'build' not found in project-list. Choose export name {exit_qsp}.\n")
			if "postprocessor" in instruction:
				# Include scripts in build instructions have priority.
				include_scripts = instruction["postprocessors"]
			elif self.include_scripts is not None:
				include_scripts = self.include_scripts
			else:
				include_scripts = None

			# Build TXT2GAM-file
			qsp.construct_file(build_files, exit_txt, self.root["preprocessor"], pp_markers)
			# Run Postprocessor if include scripts are exists.
			if include_scripts is not None:
				for script in include_scripts:
					subprocess.run([sys.executable, script, exit_txt], stdout=subprocess.PIPE)
			# Convert TXT2GAM at `.qsp`
			subprocess.run([self.converter, exit_txt, exit_qsp],stdout=subprocess.PIPE)
			if os.path.isfile(exit_qsp):
				self.export_files_paths.append(exit_qsp)
			# Delete temp file.
			if not self.save_txt2gam:
				os.remove(exit_txt)

	def run_qsp_files(self):
		self.start_file_init()

		if not os.path.isfile(self.player):
			qsp.write_error_log("error.log", f"[109] Path at player is wrong. Prove path '{self.player}'.\n")
		if not os.path.isfile(self.start_file):
			qsp.write_error_log("error.log", f"[110] Start-file is wrong. Don't start the player.\n")
		else:
			proc = subprocess.Popen([self.player, self.start_file])
			# This instruction kill the builder after 100 ms.
			# It necessary to close process in console window,
			# but player must be open above console.
			try:
				proc.wait(0.1)
			except subprocess.TimeoutExpired:
				pass

def main():
	# Default paths to converter and player.
	converter="C:\\Program Files\\QSP\\converter\\txt2gam.exe"
	player="C:\\Program Files\\QSP\\qsp570\\qspgui.exe"

	# Three commands from arguments.
	args=qsp.parse_args(sys.argv[1:])

	# -----------------------------------------------------------------------
	# args["point_file"] - start point for search `project.json`
	# args["build"] - command for build the project
	# args["run"] - command for run the project
	# -----------------------------------------------------------------------

	# Initialise of Builder:
	builder = BuildQSP(args, converter, player)
	# Run the Builder to work
	builder.build_and_run()

if __name__=="__main__":
	main()