# Converter qsps-files (only UTF-8) into game files `.qsp`.
# stand `file_path` and run script for getting QSP-format file.
# Sorry my bad English.

import sys
import os
import re

class NewQspLocations():
	"""
		qsp-locations from qsps-file
	"""
	def __init__(self, name, code=[]):
		self.name = name
		self.code = code

	def change_name(self, name):
		self.name = name

	def change_code(self, code):
		self.code = code

class NewQspsFile():
	"""
		qsps-file, separated in locations
	"""
	def __init__(self, input_file="game.qsps", output_file=""):
		self.input_file = os.path.abspath(input_file)
		self.output_folder, file_full_name = os.path.split(self.input_file)
		self.file_name = os.path.splitext(file_full_name)[0]
		if output_file != "":
			self.output_file = os.path.abspath(output_file)
		else:
			self.output_file = f"{self.output_folder}\\{self.file_name}.qsp"
		self.locations_count = 0
		self.locations = []
		self.locations_id = {}
		self.QSP_CODREMOV = 5
		if os.path.isfile(self.input_file):
			with open(self.input_file, 'r', encoding='utf-8') as file:
				self.file_strings = file.readlines()
			mode = {"location-name": ""}
			for string in self.file_strings:
				location_name = re.match(r'^\#\s?(.*?)$', string)
				close_location = re.match(r'^\-.*?$', string)
				if (mode['location-name'] == "") and (location_name is not None):
					location = NewQspLocations(location_name.group(1))
					code_strings = []
					self.locations.append(location)
					self.locations_id[location_name.group(1)] = self.locations_count
					self.locations_count += 1
					mode['location-name'] = location_name.group(1)
				elif (mode['location-name'] != "") and (close_location is None):
					code_strings.append(string)
				elif (mode['location-name'] != "") and (close_location is not None):
					location.change_code(code_strings)
					mode['location-name']=""
		else:
			print(f"File '{self.input_file}' is not exist")

	def print_locations_names(self):
		print(f'Locations number: {len(self.locations)}')
		for location in self.locations:
			print(location.name)

	def print_location(self, name=0):
		if type(name) == int:
			location_name = self.locations[name].name
			location_code = self.locations[name].code
		elif type(name) == str:
			location_name = self.locations[self.locations_id[name]].name
			location_code = self.locations[self.locations_id[name]].code
		if location_name is not None:
			print(f"'{location_name}'")
			print(location_code)

	def decode_qsps_line(self, qsps_line):
		if type(qsps_line) == int: qsps_line = str(qsps_line)
		exit_line = ""
		for point in qsps_line:
			exit_line += (chr(-self.QSP_CODREMOV) if ord(point) == self.QSP_CODREMOV else chr(ord(point) - self.QSP_CODREMOV))
		return exit_line

	def decode_location(self, code):
		exit_line = ""
		last_line = code.pop()[:-1]
		for string in code:
			exit_line += string.replace('\n', '\r\n')
		return self.decode_qsps_line(exit_line)+self.decode_qsps_line(last_line)

	def convert(self):
		new_file_strings = []
		new_file_strings.append('QSPGAME\n')
		new_file_strings.append('qsps_to_qsp SublimeText QSP Package\n')
		new_file_strings.append(self.decode_qsps_line('No')+'\n')
		new_file_strings.append(self.decode_qsps_line(self.locations_count)+'\n')
		for location in self.locations:
			new_file_strings.append(self.decode_qsps_line(location.name)+'\n\n')
			new_file_strings.append(self.decode_location(location.code)+'\n')
			new_file_strings.append(self.decode_qsps_line(0)+'\n')
		with open(self.output_file, 'w', encoding='utf-16le') as file:
			file.write(''.join(new_file_strings))

if __name__ == "__main__": 
	file = NewQspsFile(input_file="drive-.qsps")
	file.convert()
