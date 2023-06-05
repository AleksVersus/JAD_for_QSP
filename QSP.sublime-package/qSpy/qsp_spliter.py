# Sorry my Bad English.

import sys
import os
import re
import codecs

from .qsp_to_qsps import QspToQsps

class QspSplitter():
	"""
		Get QSP-file and .qproj file, convert in qsps
		and split qsps in many files, and replace them
		in other folders by .qproj-file mapping.
	"""
	def __init__(self, args={}):
		self.args = args
		if 'txt2gam-file' in self.args: self.args['qsps-file'] = self.args['txt2gam-file']
		if 'game-file' in self.args:
			# QSP-game path is getted
			self.qsp_game_path = os.path.abspath(self.args['game-file'])
			self.root_folder_path, full_file_name = os.path.split(self.qsp_game_path)
			self.file_name = os.path.splitext(full_file_name)[0]
			self.qsp_to_qsps = QspToQsps({'game-file':self.qsp_game_path})
			self.qsps_file = self.qsp_to_qsps.convert()
			self.qsp_project_file = f"{self.root_folder_path}\\{self.file_name}.qproj"
			self.output_folder = f"{self.root_folder_path}\\{self.file_name}"
			self.mode = 'game'
		elif 'qsps-file' in self.args:
			# Split other qsps-file
			self.qsps_file = os.path.abspath(self.args['qsps-file'])
			self.root_folder_path, full_file_name = os.path.split(self.qsps_file)
			self.file_name= os.path.splitext(full_file_name)[0]
			self.qsp_project_file = f"{self.root_folder_path}\\{self.file_name}.qproj"
			self.output_folder = f"{self.root_folder_path}\\{self.file_name}"
			self.mode = 'txt'
		else:
			self.mode = ''
		
	def split_file(self):
		if self.mode in ('game', 'txt'):
			if not os.path.isdir(self.output_folder):
				os.mkdir(self.output_folder)
			self.splitter(
				game_adr=self.qsps_file,
				proj_adr=self.qsp_project_file,
				export_fold=self.output_folder
			)
		else:
			self.splitter()	

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
				with open(proj_adr,"r",encoding='utf-8') as proj_file:
					proj_list=proj_file.readlines()
					for i in proj_list:
						location=re.match(r'\s*?<Location name=".*?"/>', i)
						folder=re.match(r'\s*?<Folder name=".*?">', i)
						close_folder=re.match(r'\s.*?</Folder>',i)
						if location!=None:
							name=re.search(r'name=".*?"', i).group(0)
							name=name[6:len(name)-1] # имя локации
							file_name=self.replace_bad_symbols(name)
							if folder_path=="":
								location_dict[name]=file_name+".qsps"
							else:
								location_dict[name]=folder_path+"\\"+file_name+".qsps"
						if folder!=None:
							name=re.search(r'name=".*?"', i).group(0)
							name=name[6:len(name)-1]
							folder_path=self.replace_bad_symbols(name)
						if close_folder!=None:
							folder_path=""
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
				if not os.path.isdir(f"{export_fold}\\{folder}"):
					# если дирректория не существует, создаём
					os.mkdir(f"{export_fold}\\{folder}")
				if os.path.isfile(f"{export_fold}\\{path}"):
					name, ext = os.path.splitext(path)
					path=f"{name}_{count}{ext}"
				# print(f"[160] {path}")
				with open(f"{export_fold}\\{path}","w",encoding="utf-8") as file:
					# теперь сохраняем файлы
					file.write(location_array[location_name])
			# удаляем исходный файл. delete qsps
			# os.remove(game_adr)
		else:
			print('Error. File "game.txt" is not found!')

def main():
	args = {'qsps-file':'D:\\my\\projects\\nonQSP-video\\flat_earth\\lastbugs.qsps'}
	QspSplitter(args=args).split_file()

if __name__=="__main__":
	# local start of script
	main()