# Converter qsps-files (only UTF-8) into game files `.qsp`.
# stand `file_path` and run script for getting QSP-format file.
# Sorry my bad English.

import sys
import os
import re

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
	def __init__(self, input_file="game.qsps", output_file=""):
		self.input_file = os.path.abspath(input_file)
		self.output_folder, file_full_name = os.path.split(self.input_file)
		self.file_name = os.path.splitext(file_full_name)[0]
		if output_file != "":
			self.output_file = os.path.abspath(output_file)
		else:
			self.output_file = self.output_folder+"\\"+self.file_name+".qsp"
		self.locations_count = 0
		self.locations = []
		self.locations_id = {}
		self.QSP_CODREMOV = 5
		self.file_strings = []
		if os.path.isfile(self.input_file):
			with open(self.input_file, 'r', encoding='utf-8') as file:
				self.file_strings = file.readlines()
			self.split_to_locations(self.file_strings)
		else:
			print("File '"+self.input_file+"' is not exist")

	def split_to_locations(self, string_lines):
		input_text = ''.join(string_lines)
		code_text = ""
		mode = {'location-name': ""}
		count =0
		while len(input_text)>0:
			count+=1
			scope_type, prev_text, scope_regexp_obj, post_text = self.find_overlap_main(input_text)
			if scope_type=='location-start' and mode['location-name']=='':
				location = NewQspLocation(scope_regexp_obj.group(1).replace('\r',''))
				code_text = ""
				self.locations.append(location)
				self.locations_id[scope_regexp_obj.group(1)] = self.locations_count
				self.locations_count += 1
				mode['location-name'] = scope_regexp_obj.group(1)
				input_text = post_text
			elif scope_type=='location-end' and mode['location-name']!='':
				code_text += prev_text
				input_text = post_text
				location.change_code(code_text.replace('\n','\n\r').split('\r')[1:-1])
				mode['location-name']=""
			elif scope_type=="string" and mode['location-name']!='':
				# adding code work where location is open
				code_text += prev_text + scope_regexp_obj.group(0)
				input_text = post_text
			else:
				if input_text!=post_text:
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
		for string_id in mini_data_base['scope-name']:
			i = mini_data_base['scope-name'].index(string_id)
			match_in = mini_data_base['scope-regexp'][i]
			mini_data_base['scope-instring'].append(
				string_line.index(match_in.group(0)) if match_in is not None else maximal)
		minimal = min(mini_data_base['scope-instring'])
		if minimal!=maximal:
			i = mini_data_base['scope-instring'].index(minimal)
			scope_type = mini_data_base['scope-name'][i]
			scope_regexp_obj = mini_data_base['scope-regexp'][i]
			scope = scope_regexp_obj.group(0)
			q = string_line.index(scope)
			prev_line = string_line[0:q]
			post_line = string_line[q+len(scope):]
			return scope_type, prev_line, scope_regexp_obj, post_line
		else:
			return None, '', '', string_line

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

def main():
	file = NewQspsFile(input_file="drive-.qsps")
	file.convert()

if __name__ == "__main__": 
	main()
