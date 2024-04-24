# Sorry my bad English.
import os

from .qsp_splitter import QspSplitter

class FinderSplitter():
	"""autotranslate:
		1. Search and convert all QSP files in a folder. Script:
			* finds all QSP files (files with `.qsp` extension) and all qsps files (files with `.qsps` extension) in the specified folder (current by default);
			* QSP files will convert them to qsps;
			* split into location files.
			* As a result, a folder of the same name will be created for each QSP file or qsps file, in which subfolders and location files will be placed according to the structure of the `.qproj` file. If no matching `.qproj` file is found, all locations will be placed in the same folder.
		2. Converting `game.txt`. This mode is launched if no QSP files could be found when starting the first mode.
			* The script will try to find the `game.txt` file in the specified folder.
			* If the file is found, the `export_game` folder will be created, which will contain folders and location files according to the structure of the `game.qproj` file.
			* If the file is not found, the script will exit with an error message.
	"""
	def __init__(self, folder_path="."):
		self.folder_path = os.path.abspath(folder_path)
		self.search_n_split()

	def search_n_split(self):
		path_list = [os.path.join(self.folder_path, path) for path in os.listdir(self.folder_path)]
		qsp_files_list = []
		qsps_files_list = []
		for path in path_list:
			if os.path.isfile(path):
				folder_path, full_file_name = os.path.split(path)
				file_name, file_ext = os.path.splitext(full_file_name)
				if file_ext == '.qsp':
					qsp_files_list.append(path)
				elif file_ext == '.qsps':
					qsps_files_list.append(path)
		if len(qsp_files_list)>0 or len(qsps_files_list)>0:
			for file in qsp_files_list:
				QspSplitter(args={'game-file':file}).split_file()
			for file in qsps_files_list:
				QspSplitter(args={'qsps-file':file}).split_file()
		else:
			QspSplitter().split_file()

def main():
	folder_path = "."
	FinderSplitter(folder_path=folder_path)

if __name__ == "__main__":
	main()
