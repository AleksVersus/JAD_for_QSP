# Sorry my Bad English.
import os
import re
import codecs

from .qsp_to_qsps import QspToQsps
from .qsps_to_qsp import NewQspsFile

class QspSplitter():
	"""
		Get QSP-file and .qproj file, convert in qsps
		and split qsps in many files, and replace them
		in other folders by .qproj-file mapping.
	"""
	def __init__(self) -> None:
		self.mode:str = 'game' # Literally 'game' or 'txt' (QSP or qsps -files)

		# pathes fields:
		self.qsp_game_path:str = '' # abs path to QSP-file
		self.root_folder_path:str = '' # abs path to folder where sources are lies
		self.file_name:str = '' # QSP or qsps -file name without extension
		self.file_ext:str = '' # QSP or qsps -file extension
		self.qsp_project_file:str = '' # path to .qproj-file for QSP-file
		self.output_folder:str = '' # abs path of output folder for splited files (root fold + file_name)

		self.qsps_file:str = '' # abs path to qsps-file
		
		# data fields:
		self.qsp_to_qsps:QspToQsps = None # object for converting game to qsps
		self.qproj_data:dict = {} # dict[location_name: (placement_folder, file_name)]

	def set_mode(self, new_mode:str) -> None:
		""" Set mode of splitting """
		self.mode = new_mode

	def choose_mode(self, file_ext:str=None) -> None:
		""" Choose mode by extension of file """
		if file_ext: self.file_ext = file_ext
		if self.file_ext in ('.qsp'):
			self.mode = 'game'
		elif self.file_ext in ('.qsps', '.qsp-txt', '.txt-qsp'):
			self.mode = 'txt'

	def set_input_file(self, input_file:str) -> None:
		""" Set pathes of files by mode """
		input_file = os.path.abspath(input_file)
		self.root_folder_path, full_file_name = os.path.split(input_file)
		self.file_name, self.file_ext = os.path.splitext(full_file_name)[0]
		self.output_folder = os.path.join(self.root_folder_path, self.file_name)
		self.qsp_project_file = os.path.join(self.root_folder_path, self.file_name+".qproj")
		if self.mode == 'game':
			self.qsp_game_path = input_file
		elif self.mode == 'txt':
			self.qsps_file = input_file
	
	def split_file(self, input_file:str, mode:str='game') -> None:
		""" Split the common file into separate location-files. """
		if os.path.isfile(input_file):
			self.set_mode(mode)
			self.set_input_file(input_file)
		else:
			print(f'[400] QspSplitter: File {input_file} is not exist.')
			return None
		if self.mode in ('game', 'txt'):
			os.makedirs(self.output_folder, exist_ok=True)
			self.read_qproj() # get output pathes for location placements
			if self.mode == 'game':
				self.split_game()
			else:
				self.split_qsps()
		else:
			print(f'[401] QspSplitter: mode is not setted.')

	def replace_bad_symbols(self, file_name):
		# заменяем запрещённые символы на символы подчёркивания
		file_name=re.sub(r'(&lt;|&gt;|&quot;)','_',file_name)
		file_name=re.sub(r'<','_',file_name)
		file_name=re.sub(r'>','_',file_name)
		file_name=re.sub(r'\*','_',file_name)
		file_name=re.sub(r'\\','_',file_name)
		file_name=re.sub(r'\/','_',file_name)
		file_name=re.sub(r'\:','_',file_name)
		file_name=re.sub(r'\?','_',file_name)
		file_name=re.sub(r'\|','_',file_name)
		file_name=re.sub(r'\"','_',file_name)
		return file_name

	def splitter(self, game_adr="game.txt",proj_adr="game.qproj",export_fold="export_game"):
		folder_path=""
		location_dict={} # список/словарь файлов/локаций
		location_array={} # словарь, содержащий и названия локаций и их полный текст
		if os.path.isfile(game_adr):
			# декодируем файл, убираем BOM
			byte = min(32, os.path.getsize(game_adr))
			raw = open(game_adr,'rb').read(byte)
			encoding='utf-8'
			bt=b''
			if raw.startswith(codecs.BOM_UTF8):
				encoding='utf-8'
				bt=codecs.BOM_UTF8
			elif raw.startswith(codecs.BOM_UTF16):
				encoding='utf-16'
				bt=codecs.BOM_UTF16
			if bt!=b'':
				with open(game_adr,'r',encoding=encoding) as file:
					text_game=file.read()
				with open(game_adr,'w',encoding='utf-8') as file:
					file.write(text_game)
			else:
				with open(game_adr,'r',encoding=encoding) as file:
					file.seek(0)
					text_game=file.read()
				with open(game_adr,'w',encoding='utf-8') as file:
					file.write(text_game)

			# данная часть получает словарь типа: имя_локации:размещение в папках
			if os.path.isfile(proj_adr):
				...
					#for i in location_dict:
					#	print(location_dict[i]) # тест полученных имён локаций.

			# эта часть дробит большой файл на фрагменты, каждый фрагмент помещая в словарь типа название_локации:содержимое
			with open(game_adr,"r",encoding="utf-8") as game_file:
				game_list=game_file.readlines()
				location_name=""
				for i in game_list:
					location_open=re.match(r'#\s*?.+?$',i)
					location_close=re.match(r'---\s*?.+?$',i)
					if location_open!=None:
						# мы нашли начало локации, получаем её имя
						location_name=location_open.group(0)
						location_name=re.sub(r'^#\s*','',location_name)
						location_array[location_name]=i
					elif location_close!=None:
						# мы нашли конец локации, правда ли это конец
						location_array[location_name]+=i 
						ln=location_close.group(0)
						ln=re.sub(r'^---\s+','',ln)
						ln=re.sub(r'\s-+$','',ln)
						if ln==location_name:
							location_name=""
					elif location_name!="":
						location_array[location_name]+=i

			# после того, как были составлены словарь путей и словарь локаций сохраняем файлы
			count=1
			if not os.path.isdir(export_fold):
				os.mkdir(export_fold)
			for location_name in location_array:
				if location_name in location_dict:
					# если в списке путей есть указанная локация, берём путь оттуда
					path=location_dict[location_name]
				else:
					# в противном случае сохраняем локацию в текущей папке
					path = self.replace_bad_symbols(location_name)+".qsps"
				folder=os.path.split(path)[0]
				if not os.path.isdir(os.path.join(export_fold, folder)):
					# если дирректория не существует, создаём
					os.mkdir(os.path.join(export_fold, folder))
				if os.path.isfile(os.path.join(export_fold, path)):
					name, ext = os.path.splitext(path)
					path=f"{name}_{count}{ext}"
				# print(f"[160] {path}")
				with open(os.path.join(export_fold, path),"w",encoding="utf-8") as file:
					# теперь сохраняем файлы
					file.write(location_array[location_name])
			# удаляем исходный файл. delete qsps
			# os.remove(game_adr)
		else:
			print('Error. File "game.txt" is not found!')

	def read_qproj(self) -> None:
		""" Read qproj file and fill dict by folders for locations """
		OPEN_LOCATION = re.compile(r'\s*?<Location name="(.*?)"/>')
		OPEN_FOLDER = re.compile(r'\s*?<Folder name="(.*?)">')
		CLOSE_FOLDER = re.compile(r'\s*?<\/Folder>')
		if not os.path.isfile(self.qsp_project_file):
			return None
		with open(self.qsp_project_file,"r",encoding='utf-8-sig') as fp:
			proj_lines = fp.readlines()
		current_folder = ''
		for line in proj_lines:
			location = OPEN_LOCATION.match(line)
			folder = OPEN_FOLDER.match(line)
			if location:
				loc_name = location.group(1)
				loc_file_name = self.replace_bad_symbols(loc_name)
				if not current_folder:
					output_folder = self.output_folder
				else:
					output_folder = os.path.join(self.output_folder, current_folder)
				self.qproj_data[loc_name] = (output_folder, loc_file_name)
			elif folder:
				fold_name = folder.group(1)
				current_folder = self.replace_bad_symbols(fold_name)
			elif CLOSE_FOLDER.match(line):
				current_folder = ''

	def split_game(self) -> None:
		""" Split QSP-file, convert it, and write locations as files """
		if self.mode != 'game' or not os.path.isfile(self.qsp_game_path):
			return None
		q = self.qsp_to_qsps = QspToQsps()
		q.read_from_file(self.qsp_game_path)
		q.split_qsp()
		count = {}
		for location in q.get_locations():
			output_lines = []
			loc_name = location['name']
			output_lines.append(f'QSP-Game {loc_name}\n\n')
			if loc_name in self.qproj_data:
				fold, file = self.qproj_data[loc_name]
			else:
				fold, file = self.output_folder, self.file_name
			output_path = os.path.join(fold, file + '.qsps')
			if not output_path in count: count[output_path] = 0
			if os.path.isfile(output_path):
				count[output_path] += 1
				output_path = os.path.join(fold, f'{file}_{count[output_path]}.qsps')
			os.makedirs(fold, exist_ok=True)
			output_lines.extend(QspToQsps.convert_location(location))
			with open(output_path, 'w', encoding='utf-8') as fp:
				fp.writelines(output_lines)

	def split_qsps(self) -> None:
		""" Split qsps-file and write locations as files """
		if self.mode != 'game' or not os.path.isfile(self.qsps_file):
			return None
		q = NewQspsFile()
		q.read_from_file(self.qsps_file)
		q.split_to_locations()

def main():
	args = {'qsps-file':'..\\flat_earth\\lastbugs.qsps'}
	QspSplitter(args=args).split_file()

if __name__=="__main__":
	# local start of script
	main()