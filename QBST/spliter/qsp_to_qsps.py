# Converter ".qsp" game files into qsps-files. Based on converter by Werewolf in JS.
# stand `file_path` and run script for getting qsps-format file

import sys
import os
import re

QSP_CODREMOV = 5

######### new functions ##########
def index_of(string, substring, start=0):
	if substring in string:
		return string.index(substring, start)
	else:
		return -1
######### new functions ##########

def to_qsps(locations):
	qsps_text = "QSP-Game file_name\nЧисло локаций: location_count\n"
	qsps_text += '\n\n'.join([convert_location(location) for location in locations])
	return qsps_text+'\n\n'

def convert_description(description):
	if len(description)==0:
		return ''
	else:
		lines = description.split('\r\n')
		last_line = lines.pop()
		qsps_text = ""
		for line in lines:
			qsps_text += f"*pl '{escape_qsp_string(line)}'\n"
		qsps_text += f"*p '{escape_qsp_string(last_line)}'\n"
		return qsps_text

def convert_actions(actions):
	if len(actions)==0:
		return ''
	else:
		try:
			return '\n'.join([convert_action(action) for action in actions])+'\n'
		except:
			print(actions)

def convert_action(action):
	qsps_text = f"act '{escape_qsp_string(action['name'])}'"
	image = (f", '{escape_qsp_string(action['image'])}':" if action['image']!='' else ':')
	qsps_text += image
	qsps_text += ('\n\t'+'\n\t'.join(action['code'].split('\r\n')) if action['code']!='' else '')
	qsps_text += '\nend'
	return qsps_text

def convert_location(location):
	qsps_text = f"# {location['name']}\n"
	qsps_text += f"{convert_description(location['description'])}"
	qsps_text += f"{convert_actions(location['actions'])}"
	loc_code = location['code'].replace('\r\n','\n')
	qsps_text += f"{loc_code}\n"
	qsps_text += f"--- {location['name']} ---------------------------------"
	return qsps_text

def escape_qsp_string(qsp_string):
	return qsp_string.replace("'", "''")

def split_into_lines(qsp_source_text):
	offset = 0
	lines = []
	count = 0
	while (offset < len(qsp_source_text)):
		end = index_of(qsp_source_text, '\n', start=offset)
		if end < 0:
			end = len(qsp_source_text)
		lines.append(qsp_source_text[offset:end])
		offset = end + 1
	return lines

def decode_qsp_line(qsp_line):
	exit_line = ""
	for char in qsp_line:
		exit_line += (chr(QSP_CODREMOV) if ord(char) == -QSP_CODREMOV else chr(ord(char) + QSP_CODREMOV))
	return exit_line

def decode_int(qsp_line):
	return int(decode_qsp_line(qsp_line))

def decode_string(qsp_line):
	return decode_qsp_line(qsp_line)

def read_qsp(qsp_source_text):
	header = qsp_source_text[0:7]
	if header != 'QSPGAME':
		print(f'Old qsp format is not support. Use Quest Generator for converting game in new format.')
		return []
	else:
		qsp_lines = split_into_lines(qsp_source_text)
		location_count = decode_int(qsp_lines[3])
		locations = []
		i = 4
		while (i < len(qsp_lines)):
			location_name = decode_string(qsp_lines[i])
			location_desc = decode_string(qsp_lines[i+1])
			location_code = decode_string(qsp_lines[i+2])
			i += 3
			actions = []
			actions_count = decode_int(qsp_lines[i])
			i += 1
			for j in range(actions_count):
				action_image = decode_string(qsp_lines[i])
				action_name = decode_string(qsp_lines[i+1])
				action_code = decode_string(qsp_lines[i+2])
				i += 3
				actions.append({
					"image": action_image,
					"name": action_name,
					"code": action_code
				})
			locations.append({
				"name": location_name,
				"description": location_desc,
				"code": location_code,
				"actions": actions
			})
		return locations

def main(file_path):
	exit_folder, file_full_name = os.path.split(os.path.abspath(file_path))
	file_name = os.path.splitext(file_full_name)[0]
	if os.path.isfile(file_path):
		with open(file_path, 'r', encoding='utf-16le') as file:
			qsp_source_text = file.read()
		qsps_text = to_qsps(read_qsp(qsp_source_text))
		with open(f'{exit_folder}\\{file_name}.qsps', 'w', encoding='utf-8') as file:
		 	file.write(qsps_text)
	else:
		# файл не существует
		print(f'File {file_path} is not exist.')

if __name__ == "__main__":
	file_path = "drive.qsp"
	main(file_path)
