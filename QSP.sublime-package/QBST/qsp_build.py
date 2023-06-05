# QSP-builder

# Sorry My BAD English!!!

# Build the game-files in ".qsp"-format from text-files in TXT2GAM-format.
# Собирает файлы игр формата ".qsp" из текстовых файлов формата TXT2GAM.

# Don't use this script as module! Не используйте этот скрипт, как модуль!

# Importing standart modules.
import sys, os

import sublime
import sublime_plugin

# Importing my modules from qSpy package.
from qSpy.function import parse_args
from qSpy.builder import BuildQSP

class QspBuildCommand(sublime_plugin.WindowCommand):

	def run(self, qsp_mode = "--br"):
		# Default paths to converter and player.
		converter = "qsps_to_qsp" # buil-in converter. WARNING! Test-mode!!!
		player = "C:\\Program Files\\QSP\\qsp580\\qspgui.exe"

		# Three commands from arguments.
		args = parse_args([qsp_mode, self.view.file_name()])

		# -----------------------------------------------------------------------
		# args["point_file"] - start point for search `project.json`
		# args["build"] - command for build the project
		# args["run"] - command for run the project
		# -----------------------------------------------------------------------

		# Initialise of Builder:
		builder = BuildQSP(args, converter, player)
		# Run the Builder to work:
		builder.build_and_run()