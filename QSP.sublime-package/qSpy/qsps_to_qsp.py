# Converter qsps-files (only UTF-8) into game files `.qsp`.
# stand `file_path` and run script for getting QSP-format file.
# Sorry my bad English.

import sys
import os
import re
from .function import clear_locname

class NewQspLocation():
	"""
		qsp-locations from qsps-file
	"""
	def __init__(self, name, code=None):
		self.name = name
		self.code = ([] if code == None else code)

	def change_name(self, name):
		self.name = name

	def change_code(self, code):
		self.code = code

class NewQspsFile():
	"""
		qsps-file, separated in locations
	"""
	def __init__(self, input_file:str=None, output_file:str=None, file_strings:list=None):
		"""
			initialise. 
		"""
		# main fields:
		self.locations_count = 0
		self.locations = []
		self.locations_id = {}
		self.QSP_CODREMOV = 5
		self.file_strings = []
		self.converted_strings = None # output converted strings

		# files fields
		self.input_file = input_file
		self.output_folder = None
		self.file_name = None

		# from file or filestrings
		if input_file is not None:
			# convert of exists file
			self.input_file = os.path.abspath(input_file)
			self.output_folder, file_full_name = os.path.split(self.input_file)
			self.file_name = os.path.splitext(file_full_name)[0]
			
			if os.path.isfile(self.input_file):
				with open(self.input_file, 'r', encoding='utf-8') as file:
					self.file_strings = file.readlines()
				self.file_body = ''.join(self.file_strings)
				self.split_to_locations(self.file_strings)
			else:
				print(f'File «{self.input_file}» is not exist')
		else:
			# covert of data
			self.file_strings = file_strings

		if output_file is not None:
			self.output_file = os.path.abspath(output_file)
		elif not None in (self.output_folder, self.file_name):
			self.output_file = os.path.join(self.output_folder, self.file_name+".qsp")

	def split_to_locations(self, string_lines:list):
		input_text = ''.join(string_lines)
		location_code = ""
		mode = {'location-name': ""}
		while len(input_text) > 0:
			scope_type, prev_text, scope_regexp_obj, post_text = self.find_overlap_main(input_text)
			if scope_type=='location-start' and mode['location-name']=='':
				location = NewQspLocation(scope_regexp_obj.group(1).replace('\r',''))
				location_code = ""
				self.locations.append(location)
				self.locations_id[scope_regexp_obj.group(1)] = self.locations_count
				self.locations_count += 1
				mode['location-name'] = scope_regexp_obj.group(1)
				input_text = post_text
			elif scope_type=='location-end' and mode['location-name']!='':
				location_code += prev_text
				input_text = post_text
				location.change_code(location_code.replace('\n','\n\r').split('\r')[1:-1])
				mode['location-name'] = ""
			elif scope_type == "string" and mode['location-name']!='':
				# adding code work where location is open
				location_code += prev_text + scope_regexp_obj.group(0)
				input_text = post_text
			elif scope_type == 'string' and mode['location-name']=='':
				# open string between locations
				# change input text from next symbol
				input_text = input_text[scope_regexp_obj.end():]
			else:
				if input_text != post_text:
					input_text = post_text
				else:
					input_text = ''

	def find_overlap_main(self, string_line:str):
		maximal = len(string_line)+1
		mini_data_base = {
			"scope-name": [
				'location-start',
				'location-end',
				'string'
			],
			"scope-regexp":
			[
				re.search(r'^\#\s?(.*?)$', string_line, flags=re.MULTILINE),
				re.search(r'^\-.*$', string_line, flags=re.MULTILINE),
				re.search(r'("|\')[\S\s]*?(\1)', string_line, flags=re.MULTILINE)
			],
			"scope-instring":
			[]
		}
		for i, string_id in enumerate(mini_data_base['scope-name']):
			match_in = mini_data_base['scope-regexp'][i]
			mini_data_base['scope-instring'].append(
				match_in.start() if match_in is not None else maximal)
		minimal = min(mini_data_base['scope-instring'])
		if minimal!=maximal:
			i = mini_data_base['scope-instring'].index(minimal)
			scope_type = mini_data_base['scope-name'][i]
			scope_regexp_obj = mini_data_base['scope-regexp'][i]
			scope = scope_regexp_obj.group(0)
			q = scope_regexp_obj.start()
			prev_line = string_line[0:q]
			post_line = string_line[q+len(scope):]
			return scope_type, prev_line, scope_regexp_obj, post_line
		else:
			return None, '', '', string_line

	def get_qsplocs(self):
		qsp_locs = []
		for location in self.locations:
			re_name = clear_locname(location.name)
			match = re.search(r'^\#\s*('+re_name+')$', self.file_body, flags=re.MULTILINE)
			if not match is None:
				qsp_locs.append([location.name, [match.start(1), match.end(1)]])
		return qsp_locs

	def print_locations_names(self):
		print('Locations number: '+str(len(self.locations)))
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
			print("'"+location_name+"'")
			print(location_code)

	def decode_qsps_line(self, qsps_line):
		if type(qsps_line) == int: qsps_line = str(qsps_line)
		exit_line = ""
		for point in qsps_line:
			exit_line += (chr(-self.QSP_CODREMOV) if ord(point) == self.QSP_CODREMOV else chr(ord(point) - self.QSP_CODREMOV))
		return exit_line

	def decode_location(self, code):
		if len(code)>0:
			exit_line = ""
			last_line = code.pop()[:-1]
			for string in code:
				exit_line += string.replace('\n', '\r\n')
			return self.decode_qsps_line(exit_line)+self.decode_qsps_line(last_line)
		else:
			return ""

	def convert(self):
		if self.converted_strings is not None:
			print('[301] Already converted.')
			raise Exception('[301] Already converted.')
			return None
		self.converted_strings = []
		self.converted_strings.append('QSPGAME\n')
		self.converted_strings.append('qsps_to_qsp SublimeText QSP Package\n')
		self.converted_strings.append(self.decode_qsps_line('No')+'\n')
		self.converted_strings.append(self.decode_qsps_line(self.locations_count)+'\n')
		for location in self.locations:
			self.converted_strings.append(self.decode_qsps_line(location.name)+'\n\n')
			self.converted_strings.append(self.decode_location(location.code)+'\n')
			self.converted_strings.append(self.decode_qsps_line(0)+'\n')
	
	def save_qsps(self, input_file:str=None) -> None:
		if self.input_file is None and input_file is None:
			print('[302] Not input path.')
			raise Exception('[302] Not input path.')
			return None
		if input_file is None:
			input_file = self.input_file
		with open(input_file, 'w', encoding='utf-16le') as file:
			file.write(''.join(self.file_strings))

	def save_qsp(self, output_file:str=None) -> None:
		if self.output_file is None and output_file is None:
			print('[303] Not output path.')
			raise Exception('[303] Not output path.')
			return None
		if output_file is None:
			output_file = self.output_file
		with open(output_file, 'w', encoding='utf-16le') as file:
			file.write(''.join(self.converted_strings))

def main():
	file = NewQspsFile(input_file="example.qsps")
	file.convert()

if __name__ == "__main__": 
	main()
