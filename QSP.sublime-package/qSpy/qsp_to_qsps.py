# python 3.8
import os

class QspToQsps():
	"""Converter ".qsp" game files into qsps-files. Based on converter by Werewolf in JS.
	stand `game-file` and run script for getting qsps-format file"""
	def __init__(self, args:dict=None) -> None:
		if args is None: args = {}
		self.QSP_CODREMOV = 5 # type: int # constant
		self.args = args # type: dict
		if 'game-file' in self.args:
			self.input_file = os.path.abspath(args['game-file'])
			self.output_folder, file_full_name = os.path.split(self.input_file)
			self.file_name = os.path.splitext(file_full_name)[0]
		else:
			self.input_file = "" # type: str
			self.output_folder = "" # type: str
			self.file_name = "" # type: str
		self.location_count = 0 # type: int
		self.locations = [] # type: list
		self.qsp_source_text = '-' * 7 # type: str
		self.qsps_text = "" # type: str
		self.pasword = "" # type: str

	def convert(self) -> str:
		""" Read qsp-file, convert and save to qsps-file. Return path to qsps-file. """
		if os.path.isfile(self.input_file):
			with open(self.input_file, 'r', encoding='utf-16le') as file:
				self.qsp_source_text = file.read()
			self.read_qsp()
			output_file = os.path.join(self.output_folder, self.file_name+'.qsps')
			with open(output_file, 'w', encoding='utf-8') as file:
				file.write(self.to_qsps())
			return output_file
		else:
			print(f'File {self.input_file} is not exist.')

	def read_qsp(self) -> None:
		""" Split qsp-source on locations and convert them to qsps-format. """
		header = self.qsp_source_text[0:7]
		if header != 'QSPGAME':
			print(f'Old qsp format is not support. Use Quest Generator for converting game in new format.')
		else:
			qsp_lines = self.split_into_lines(self.qsp_source_text)
			self.password = self.decode_string(qsp_lines[2])
			self.location_count = self.decode_int(qsp_lines[3])
			i = 4
			while (i < len(qsp_lines)):
				location_name = self.decode_string(qsp_lines[i])
				location_desc = self.decode_string(qsp_lines[i+1])
				location_code = self.decode_string(qsp_lines[i+2])
				i += 3
				actions = []
				actions_count = self.decode_int(qsp_lines[i])
				i += 1
				for _ in range(actions_count):
					action_image = self.decode_string(qsp_lines[i])
					action_name = self.decode_string(qsp_lines[i+1])
					action_code = self.decode_string(qsp_lines[i+2])
					i += 3
					actions.append({
						"image": action_image,
						"name": action_name,
						"code": action_code
					})
				self.locations.append({
					"name": location_name,
					"description": location_desc,
					"code": location_code,
					"actions": actions
				})

	def to_qsps(self) -> str:
		""" Convert all game's locations to qsps-format. """
		if not self.locations:
			return 'QSP-Game is not formed. Prove QSP-file.'
		else:
			self.qsps_text = f"QSP-Game {self.file_name}\nЧисло локаций: {self.location_count}\n"
			self.qsps_text += f"Пароль на исходном файле: {self.password}\n"
			self.qsps_text += '\n\n'.join([self.convert_location(loc) for loc in self.locations])
			return self.qsps_text+'\n\n'

	def convert_location(self, location:dict) -> str:
		""" Convert location to qsps-format. """
		qsps_text = f"# {location['name']}\n"
		qsps_text += f"{self.convert_description(location['description'])}"
		qsps_text += f"{self.convert_actions(location['actions'])}"
		loc_code = location['code'].replace('\r\n','\n')
		qsps_text += f"{loc_code}\n"
		qsps_text += f"--- {location['name']} ---------------------------------"
		return qsps_text

	def convert_description(self, description:str) -> str:
		""" Convert location description to qsps-format. """
		if not description:
			return ''
		else:
			lines = description.split('\r\n')
			last_line = lines.pop()
			qsps_text = ""
			for line in lines:
				qsps_text += f"*pl '{self.escape_qsp_string(line)}'\n"
			qsps_text += f"*p '{self.escape_qsp_string(last_line)}'\n"
			return qsps_text

	def convert_actions(self, actions:list) -> str:
		""" Convert all location's actions to qsps-format. """
		if not actions:
			return ''
		else:
			try:
				return '\n'.join([self.convert_action(action) for action in actions])+'\n'
			except:
				print(actions)

	def convert_action(self, action:dict) -> str:
		""" Convert location's action to qsps-format. """
		qsps_text = f"act '{self.escape_qsp_string(action['name'])}'"
		image = (f", '{self.escape_qsp_string(action['image'])}':" if action['image']!='' else ':')
		qsps_text += image
		qsps_text += ('\n\t'+'\n\t'.join(action['code'].split('\r\n')) if action['code']!='' else '')
		qsps_text += '\nend'
		return qsps_text

	def escape_qsp_string(self, qsp_string:str) -> str:
		""" Escape-sequence for qsp-string. """
		return qsp_string.replace("'", "''")

	def split_into_lines(self, qsp_source_text:str) -> list:
		""" Split qsp-source on lines. """
		offset = 0
		lines = []
		while (offset < len(qsp_source_text)):
			end = self.index_of(qsp_source_text, '\n', start=offset)
			if end < 0:
				end = len(qsp_source_text)
			lines.append(qsp_source_text[offset:end])
			offset = end + 1
		return lines

		if substring in string:
	def index_of(self, string:str, substring:str, start:int=0) -> int:
			return string.index(substring, start)
		else:
			return -1

	def decode_qsp_line(self, qsp_line:str) -> str:
		exit_line = ""
		for char in qsp_line:
			exit_line += (chr(self.QSP_CODREMOV) if ord(char) == -self.QSP_CODREMOV else chr(ord(char) + self.QSP_CODREMOV))
		return exit_line

	def decode_int(self, qsp_line:str) -> int:
		return int(self.decode_qsp_line(qsp_line))

	def decode_string(self, qsp_line:str) -> str:
		return self.decode_qsp_line(qsp_line)

		
def main():
	qsp_to_qsps = QspToQsps(args = {'game-file': 'Киберия.qsp'})
	qsp_to_qsps.convert()

if __name__ == "__main__":
	# 
	# main()
	# if you need choose converter for decode gamepass:
	print(QspToQsps().decode_string(f'2230/4.31'))
