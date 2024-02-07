import sublime
import sublime_plugin

import sys, os
import re
import json

# Importing my modules from qSpy package.
from .qSpy.function import parse_args
from .qSpy.function import search_project_folder
from .qSpy.function import get_files_list
from .qSpy.builder import BuildQSP
from .qSpy.qsp_to_qsps import QspToQsps
from .qSpy.qsps_to_qsp import NewQspsFile
from .qSpy.qsp_splitter import QspSplitter
from .qSpy.main_cs import FinderSplitter

# inner classes and functions
def _safe_mk_fold(new_path:str) -> None:
	""" Safe make dir with making all chain of dir """
	if not os.path.isdir(new_path):
		os.makedirs(new_path)

class QspWorkspace:
	def __init__(self) -> None:
		# microbase of locations
		self.loc_names = [] # names of location [str]
		self.loc_regions = [] # regions of locs initiate list[start, end]
		self.loc_places = [] # file path, where is qsp_locs [str]
		self.files_paths = [] # all files in project

	def hold_init(self, project_folder=None):
		if not project_folder is None:
			self.refresh_files_paths()

	def add_loc(self, name:str, region:tuple, place:str) -> int:
		self.loc_names.append(name)
		self.loc_regions.append(region)
		self.loc_places.append(place)
		return len(self.loc_names)-1

	def del_loc_by_place(self, loc_place:str) -> None:
		""" del location by place """
		if loc_place in self.loc_places:
			i = self.loc_places.index(loc_place)
			del self.loc_places[i]
			del self.loc_names[i]
			del self.loc_regions[i]

	def del_all_locs_by_place(self, loc_place:str) -> None:
		""" del all locations by place """
		while loc_place in self.loc_places:
			i = self.loc_places.index(loc_place)
			del self.loc_places[i]
			del self.loc_names[i]
			del self.loc_regions[i]

	def extract_from_file(self, project_folder=None) -> None:
		if project_folder is None:
			return None
		ws_path = os.path.join(project_folder,'qsp-project-workspace.json')
		if not os.path.isfile(ws_path):
			return None
		with open(ws_path, "r", encoding="utf-8") as ws_file:
			qsp_ws = json.load(ws_file)
		if len(self.loc_names)>0:
			self.__init__()
			print('Error: QSP WORKSPACE already initialised!!!')
		for path, qsp_locs in qsp_ws['locations'].items():
			for name, region in qsp_locs:
				self.add_loc(name, region, path)
		self.files_paths = qsp_ws['files_paths']

	def refresh_files_paths(self) -> None:
		project_folder = QspWorkspace.get_cur_pf()
		if project_folder is None:
			return None
		project_data = sublime.active_window().project_data()
		old = self.files_paths[:]
		new = []
		folders = project_data['folders']
		for pf in folders:
			if os.path.abspath(os.path.join(project_folder, pf['path'])) == project_folder:
				pf_ = project_folder
			else:
				pf_ = pf['path']
			if os.path.commonprefix([project_folder, pf_]) == '':
				break
			new.extend(get_files_list(pf_))
		self.files_paths = new
		old_set = set(old)
		new_set = set(new)
		to_del = list(old_set - new_set)
		to_add = list(new_set - old_set)
		for path in to_del:
			self.del_all_locs_by_place(os.path.relpath(path, project_folder))
		for path in to_add:
			relpath = os.path.relpath(path, project_folder)
			for loc_name, loc_region in NewQspsFile(path).get_qsplocs():
				self.add_loc(loc_name, loc_region, relpath)

	def refresh_locs_from_symbols(self, view) -> None:
		"""	Return list of QSP-locations created on this view """
		current_qsps, project_folder = QspWorkspace.get_main_pathes(view)
		if current_qsps is None or project_folder is None:
			return None
		qsps_relpath = os.path.relpath(current_qsps, project_folder)
		self.del_all_locs_by_place(qsps_relpath)
		for s in view.symbols():
			region, name = s
			if name.startswith('Локация: '):
				self.add_loc(name[9:], [region.begin(), region.end()], qsps_relpath)

	def get_json_struct(self) -> dict:
		qsp_ws_out = { 'locations': {}, 'files_paths': self.files_paths }
		qsp_locs = qsp_ws_out['locations']
		for i, path in enumerate(self.loc_places):
			if not path in qsp_locs: qsp_locs[path] = []
			qsp_locs[path].append([self.loc_names[i], self.loc_regions[i]])
		return qsp_ws_out

	def save_to_file(self, project_folder=None):
		project_folder = QspWorkspace.get_cur_pf(project_folder)
		if project_folder is None:
			return None
		qsp_workspace = self.get_json_struct()
		with open(os.path.join(project_folder, 'qsp-project-workspace.json'), "w", encoding="utf-8") as ws_file:
			json.dump(qsp_workspace, ws_file, indent=4)

	def get_locs(self):
		return zip(self.loc_names, self.loc_regions, self.loc_places)

	@staticmethod
	def get_cur_pf(project_folder=None): # -> str or None 
		if not project_folder is None:
			return project_folder
		argv = sublime.active_window().extract_variables()
		return (argv['folder'] if 'folder' in argv else None)

	@staticmethod
	def get_main_pathes(view):
		current_qsps = view.file_name()
		argv = sublime.active_window().extract_variables()
		project_folder = (argv['folder'] if 'folder' in argv else None)
		return current_qsps, project_folder

	@staticmethod
	def get_all_qsplocs(view):
		all_qsplocs = []
		argv = sublime.active_window().extract_variables()
		project_folder = (argv['folder'] if 'folder' in argv else None)
		if project_folder in QSP_WORKSPACES:
			# if ws exist in dict of wss
			qsp_ws = QSP_WORKSPACES[project_folder]
			qsp_ws.refresh_locs_from_symbols(view)
			all_qsplocs = qsp_ws.get_locs()
		else:
			# if ws dont exist in dict of wss
			for s in view.symbols():
				region, name = s
				if name.startswith('Локация: '):
					all_qsplocs.add_loc((name[9:], [region.begin(), region.end()], ''))
		return all_qsplocs

	@staticmethod
	def get_qsplabels_from_symbols(view, exclude_inputting=None): # View, Region -> list
		"""
			Return list of QSP-labels created on this view
		"""
		qsp_labels = []
		for s in view.symbols():
			region, name = s
			if exclude_inputting is None or region != exclude_inputting:
				if name.startswith('Метка: '):
					qsp_labels.append(name[7:])
		return(qsp_labels)

# constants
CMD_TEMPLATES = {
	# operators
	"inclib": "INCLIB [$путь к игре] — добавить к игре локации из указанного файла QSP.",
	"goto": "GOTO [$локация], [аргументы...] — переход на локацию с указанным названием.",
	"xgoto": "XGOTO [$локация], [аргументы...] — переход на локацию без очистки основного описания.",
	"gt": "GT [$локация], [аргументы...] — переход на локацию с указанным названием.",
	"xgt": "XGT [$локация], [аргументы...] — переход на локацию без очистки основного описания.",
	"freelib": "FREELIB — удаление из игры всех локаций, загруженных с помощью inclib.",
	"openqst": "OPENQST [$путь к игре] —замена всех локаций текущей игры локациями из укзанного файла QSP.",
	"opengame": "OPENGAME [$путь к сохранению] — загрузка указанного файла сохранения.",
	"savegame": "SAVEGAME [$путь к сохранению] запись состояния игры в указанный файл сохранения.",
	"addobj": "ADDOBJ [$название], [$картинка], [#позиция] — добавление предмета с картинкой в указанную позицию.",
	"delobj": "DELOBJ [$название] — удаление предмета с указанным названием из окна предметов.",
	"killobj": "KILLOBJ [#номер] — удаление предмета, расположенного в заданной позиции.",
	"*clr": "*CLR — очищает окно основного описания.",
	"*clear": "*CLEAR — очищает окно основного описания.",
	"*nl": "*NL [$текст] — переход на новую строку, затем вывод текста в окне основного описания.",
	"*p": "*P [$текст] — вывод текста в окно основного описания без перехода на новую строку.",
	"*pl": "*PL [$текст] — вывод текста в окно основного описания, затем переход на новую строку.",
	"act": "ACT [$название], [$картинка]: [операторы...] — создаёт и выводит в окно действий новое действие.",
	"cla": "CLA - удаляет все действия из окна действий.",
	"clr": "CLR — очищает окно дополнительного описания.",
	"clear": "CLEAR — очищает окно дополнительного описания.",
	"all": "CLOSE ALL — закрывает все проигрываемые звуковые файлы.",
	"close": "CLOSE [$звуковой файл] — останавливает проигрывание указанного звукового файла.",
	"cls": "CLS — очищает все окна кроме списка предметов.",
	"cmdclear": "CMDCLEAR — очистка строки ввода.",
	"cmdclr": "CMDCLR` — очистка строки ввода.",
	"copyarr": "COPYARR [$приёмник],[$источник],[#начало],[#количество] — копирование одного массива в другой.",
	"delact": "DELACT [$название] — удаляет действие с указанным названием.",
	"dynamic": "DYNAMIC [$код], [аргументы...] — выполняет код, переданный в виде строки текста.",
	"exit": "EXIT — прерывает выполнение текущего блока кода (локации, динамического кода и пр.).",
	"gosub": "GOSUB [$локация], [аргументы...] — вызов локации без перехода на неё.",
	"gs": "GS [$локация], [аргументы...] — вызов локации без перехода на неё.",
	"if": "IF [#выражение]: [оператор1] & ... ELSE [оператор3] & ... - конструкция условия.",
	"else": "IF [#выражение]: [оператор1] & ... ELSE [оператор3] & ... - конструкция условия.",
	"elseif": "ELSEIF [#выражение]:[оператор1] & [оператор2] & ... - альтернативное условие.",
	"jump": "JUMP [$метка] — переход на указанную метку.",
	"killall": "KILLALL — уничтожает все переменные и удаляет все предметы из окна предметов.",
	"killvar": "KILLVAR [$название массива],[индекс элемента] — удаление элемента массива по указанному индексу.",
	"menu": "MENU [$название массива] — показывает всплывающее меню с заданным названием.",
	"msg": "MSG [сообщение] — выводит диалоговое окно с сообщением.",
	"nl": "NL [$текст] — переход на новую строку, затем вывод текста в окне дополнительного описания.",
	"p": "P [$текст] — вывод текста в окно дополнительного описания без перехода на новую строку.",
	"pl": "PL [$текст] — вывод текста в окно дополнительного описания, затем переход на новую строку.",
	"play": "PLAY [$звуковой файл], [#громкость] — воспроизводит звуковой файл.",
	"refint": "REFINT — принудительное обновление интерфейса.",
	"settimer": "SETTIMER [#выражение] — задаёт интервал обращения к локации-счётчику в миллисекундах.",
	"showacts": "SHOWACTS [#выражение] — управляет отображением окна действий.",
	"showstat": "SHOWSTAT [#выражение] — управляет отображением окна дополнительного описания.",
	"showobjs": "SHOWOBJS [#выражение] — управляет отображением окна предметов.",
	"showinput": "SHOWINPUT [#выражение] — управляет отображением строки ввода (командной строки).",
	"unselect": "UNSELECT — снимает выделение с предмета.",
	"unsel": "UNSEL — снимает выделение с предмета.",
	"view": "VIEW [$путь к графическому файлу] — выводит на экран указанное изображение.",
	"wait": "WAIT [#миллисекунды] — приостанавливает выполнение кода программы.",
	"exec": "EXEC([строка кода не на QSP, которая выполнится из-под QSP])",
	"loop": "LOOP [команды перед началом цикла] - команды перед началом выполнения цикла",
	"while": "WHILE [#выражение] — цикл будет выполняться, пока выражение верно",
	"step": "STEP [команды во время цикла] — команды, которые будут выполняться на каждом проходе цикла. Здесь можно указать изменения счётчика.",
	"end": "END - завершение многострочной формы IF / ACT / LOOP.",
	# operands
	"and": "[#выражение 1] AND [#выражение 2] - логическое И.",
	"or": "[#выражение 1] OR [#выражение 2] - логическое ИЛИ.",
	"no": "NO [#выражение] - логическое отрицание.",
	"mod": "[#выражение 1] MOD [#выражение 2] - вычисление остатка от деления.",
	# functions
	"obj": "OBJ [$предмет] - проверка наличия предмета в рюкзаке.",
	"loc": "LOC [$локация] - проверка существования локации.",
	"$desc": "$DESC([$выражение]) - возвращает текст базового описания локации",
	"iif": "IIF([#выражение],[выражение_да],[выражение_нет]) - возвращает одно из выражений по условию",
	"$iif": "$IIF([#выражение],[выражение_да],[выражение_нет]) - возвращает одно из выражений по условию",
	"$input": "$INPUT([выражение]) - показывает окно ввода текста и возвращает введенное значение",
	"isplay": "ISPLAY([$выражение]) - проверяет, проигрывается ли в текущий момент указанный файл",
	"max": "MAX([выражение 1],[выражение 2], ...) - возвращает максимальное из значений аргументов",
	"$max": "$MAX([выражение 1],[выражение 2], ...) - возвращает максимальное из значений аргументов",
	"min": "MIN([выражение 1],[выражение 2], ...) - возвращает минимальное из значений аргументов",
	"$min": "$MIN([выражение 1],[выражение 2], ...) - возвращает минимальное из значений аргументов",
	"rand": "RAND([#выражение 1],[#выражение 2]) - возвращает случайное число между заданными",
	"rgb": "RGB([#красный],[#зеленый],[#синий]) - возвращает код цвета на основе 3-х составляющих",
	"$getobj": "$GETOBJ([#позиция]) - возвращает название предмета, расположенного в заданной позиции",
	"dyneval": "DYNEVAL([$выражение],[параметр 1],[параметр 2], ...) - возвращает значение динамически вычисленного выражения",
	"$dyneval": "$DYNEVAL([$выражение],[параметр 1],[параметр 2], ...) - возвращает значение динамически вычисленного выражения",
	"func": "FUNC([$выражение],[параметр 1],[параметр 2], ...) - обработка указанной локации как функции",
	"$func": "$FUNC([$выражение],[параметр 1],[параметр 2], ...) - обработка указанной локации как функции",
	"arrsize": "ARRSIZE([$выражение]) - возвращает число элементов в указанном массиве",
	"arrpos": "ARRPOS([$имя массива],[значение],[#начальный индекс]) - поиск в массиве элемента с заданным значением",
	"arritem": "ARRITEM([$имя массива],[индекс]) - возвращает значение указанной ячейки указанного массива.",
	"instr": "INSTR([$текст],[$искомый текст],[#начальная позиция]) - поиск вхождения текста",
	"isnum": "ISNUM([$выражение]) - проверяет, является ли указанная строка числом",
	"$trim": "$TRIM([$выражение]) - удаляет из текста прилегающие пробелы и символы табуляции",
	"$ucase": "$UCASE([$выражение]) - преобразует маленькие буквы текста в большие",
	"$lcase": "$LCASE([$выражение]) - преобразует большие буквы текста в маленькие",
	"len": "LEN([$выражение]) - возвращает длину указанной строки",
	"$mid": "$MID([$текст],[#начало],[#длина]) - вырезает из текста строку указанной длины начиная с заданной позиции",
	"$replace": "$REPLACE([$текст],[$искомый текст],[$текст для замены]) - заменяет в тексте заданную строку",
	"$str": "$STR([#выражение]) - переводит число в строку",
	"val": "VAL([$выражение]) - переводит строку в число",
	"arrcomp": "ARRCOMP([$имя массива],[$шаблон],[#начальный индекс]) - поиск в массиве элемента, соответствующего регулярному выражению",
	"strcomp": "STRCOMP([$выражение],[$шаблон]) - проверяет заданный текст на соответствие регулярному выражению",
	"$strfind": "$STRFIND([$выражение],[$шаблон],[#номер]) - возвращает подстроку, соответствующую группе с номером [#номер] регулярного выражения",
	"strpos": "STRPOS([$выражение],[$шаблон],[#номер]) - возвращает позицию подстроки, соответствующей группе с номером [#номер] регулярного выражения",
	"countobj": "COUNTOBJ - возвращает текущее число предметов",
	"msecscount": "MSECSCOUNT - возвращает количество миллисекунд, прошедших с момента начала игры",
	"rnd": "RND - возвращает случайное значение от 1 до 1000",
	"$curloc": "$CURLOC - возвращает название текущей локации",
	"$qspver": "$QSPVER - возвращает версию интерпретатора",
	"$selobj": "$SELOBJ - возвращает название выделенного предмета",
	"$selact": "$SELACT - возвращает название выделенного действия",
	"$curacts": "$CURACTS - возвращает в виде кода все текущие действия",
	"$user_text": "$USER_TEXT - возвращает текст в строке ввода",
	"$usrtxt": "$USRTXT - возвращает текст в строке ввода",
	"$maintxt": "$MAINTXT - возвращает текст в основном окне описания",
	"$stattxt": "$STATTXT - возвращает текст в дополнительном окне описания",
	# init vars
	"set": "SET [название переменной]=[выражение] — установка значения переменной.",
	"local": "LOCAL [название переменной]=[выражение] — назначение локальной переменной.",
	# variables
	"args": "ARGS - массив с параметрами процедуры / функции",
	"$args": "$ARGS - массив с параметрами процедуры / функции",
	"result": "RESULT - переменная содержит результат, возвращаемый текущей функцией",
	"$result": "$RESULT - переменная содержит результат, возвращаемый текущей функцией",
	"disablescroll": "DISABLESCROLL - если переменная не равна 0, то запрещает автопрокрутку текста при выводе",
	"nosave": "NOSAVE - если переменная не равна 0, то сохранение состояния игры пользователем невозможно",
	"debug": "DEBUG - если переменная не равна 0, то отключается проверка идентификатора игры при загрузке состояния",
	"$counter": "$COUNTER - переменная содержит название локации-счётчика",
	"$ongload": "$ONGLOAD - переменная содержит название локации-обработчика загрузки состояния",
	"$ongsave": "$ONGSAVE - переменная содержит название локации-обработчика сохранения состояния",
	"$onnewloc": "$ONNEWLOC - переменная содержит название локации-обработчика перехода на новую локацию",
	"$onactsel": "$ONACTSEL - переменная содержит название локации-обработчика выбора действия",
	"$onobjsel": "$ONOBJSEL - переменная содержит название локации-обработчика выбора предмета",
	"$onobjadd": "$ONOBJADD - переменная содержит название локации-обработчика добавления предмета",
	"$onobjdel": "$ONOBJDEL - переменная содержит название локации-обработчика удаления предмета",
	"$usercom": "$USERCOM - переменная содержит название локации-обработчика строки ввода",
	"usehtml": "USEHTML - если переменная не равна 0, то включает возможность использования HTML",
	"bcolor": "BCOLOR - переменная содержит цвет фона",
	"fcolor": "FCOLOR - переменная содержит основной цвет шрифта",
	"lcolor": "LCOLOR - переменная содержит основной цвет ссылок",
	"fsize": "FSIZE - переменная содержит основной размер шрифта",
	"$fname": "$FNAME - переменная содержит название основного шрифта",
	"$backimage": "$BACKIMAGE - переменная содержит путь к фоновому изображению",
}

# variables
QSP_WORKSPACES = {} # all qsp workspaces add to this dict, if you open project
QSP_TRYER = True
QSP_TEMP = {}

class QspBuildCommand(sublime_plugin.WindowCommand):
	"""
		QSP-Game Builder. Build and run QSP-game from sources. Need a project.json.
	"""
	def run(self, qsp_mode = "--br"):
		# Default paths to converter and player.
		converter = "qsps_to_qsp" # buil-in converter. WARNING! Test-mode!!!
		player = "C:\\Program Files\\QSP\\qsp580\\qspgui.exe"

		# Three commands from arguments.
		argv = self.window.extract_variables()
		args = parse_args([qsp_mode, argv['file']])

		# -----------------------------------------------------------------------
		# args["point_file"] - start point for search `project.json`
		# args["build"] - command for build the project
		# args["run"] - command for run the project
		# -----------------------------------------------------------------------

		# Initialise of Builder:
		builder = BuildQSP(args, converter, player)
		# Run the Builder to work:
		builder.build_and_run()

class QspToQspsCommand(sublime_plugin.WindowCommand):
	""" Command to start converting QSP-file to qsps """
	def run(self):
		argv = self.window.extract_variables()
		file = argv['file']
		if argv['file_extension'] == 'qsp':
			qsp_to_qsps = QspToQsps(args = {'game-file': file})
			qsp_to_qsps.convert()
		else:
			print('Wrong extension of file. Can not convert.')

class QspsToQspCommand(sublime_plugin.WindowCommand):

	def run(self):
		argv = self.window.extract_variables()
		if argv['file_extension'] in ('qsps', 'qsp-txt', 'txt-qsp'):
			file = NewQspsFile(input_file = argv['file'])
			file.convert()
		else:
			print('Wrong extension of file. Can not convert.')

class QspSplitterCommand(sublime_plugin.WindowCommand):

	def run(self):
		argv = self.window.extract_variables()
		if argv['file_extension'] in ('qsps', 'qsp-txt', 'txt-qsp'):
			QspSplitter(args = {'qsps-file': argv['file']}).split_file()
		elif argv['file_extension'] == 'qsp':
			QspSplitter(args = {'game-file': argv['file']}).split_file()
		else:
			print('Wrong extension of file. Can not convert.')

class QspSplitProjectCommand(sublime_plugin.WindowCommand):

	def run(self):
		argv = self.window.extract_variables()
		FinderSplitter(folder_path = argv['file_path'])

class QspNewProjectCommand(sublime_plugin.WindowCommand):

	def run(self):
		argv = self.window.extract_variables()
		if 'folder' in argv:
			jont = os.path.join
			_safe_mk_fold(jont(argv['folder'],'[disdocs]'))
			_safe_mk_fold(jont(argv['folder'], '[output_game]\\assets\\img'))
			_safe_mk_fold(jont(argv['folder'], '[output_game]\\assets\\snd'))
			_safe_mk_fold(jont(argv['folder'], '[output_game]\\assets\\vid'))
			_safe_mk_fold(jont(argv['folder'], '[output_game]\\lib'))
			_safe_mk_fold(jont(argv['folder'], '[source]'))
			# crete project.json
			project_json_path = jont(argv['folder'], '[source]\\project.json')
			if not os.path.isfile(project_json_path):
				project_json = [
					'{\n\t"project":\n\t[\n\t\t{\n\t\t\t"build":"..\\\\[output_game]\\\\game_start.qsp"',
					',\n\t\t\t"folders":\n\t\t\t[\n\t\t\t\t{"path":"."}\n\t\t\t]\n\t\t}',
					'\n\t],\n\t"start":"..\\\\[output_game]\\\\game_start.qsp"',
					',\n\t"player":"C:\\\\Program Files\\\\QSP\\\\qsp580\\\\qspgui.exe"\n}'
				]
				with open(project_json_path, 'w', encoding='utf-8') as file:
					file.writelines(project_json)
			# create sublime-project
			path, fname = os.path.split(argv['folder'])
			sublproj_path = jont(argv['folder'], fname + '.sublime-project')
			if not os.path.isfile(sublproj_path):
				sublime_project = [
					'{\n\t"folders":\n\t[\n\t\t{\n\t\t\t"path": ".",\n\t\t}\n\t]\n}'
				]
				with open(sublproj_path, 'w', encoding='utf-8') as file:
					file.writelines(sublime_project)
			# create startfile
			start_file_path = jont(argv['folder'], '[source]\\00_start.qsps')
			if not os.path.isfile(start_file_path):
				start_file = [
					'QSP-Game Start game from this location\n\n',
					'# [start]\n',
					'*pl "Quick project start location. Edit this file, and appending new."\n',
					'*pl "Стартовая локация быстрого проекта. ',
					'Отредактируйте этот файл и добавьте новые."\n',
					'--- [start] ---\n'
				]
				with open(start_file_path, 'w', encoding='utf-8') as file:
					file.writelines(start_file)
				self.window.open_file(start_file_path)

class QspNewGameHeadCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		self.view.insert(edit, 0, 'QSP-Game .New qsps-file.\n\n')

class QspNewGameCommand(sublime_plugin.WindowCommand):
	def run(self):
		new_view = self.window.new_file(syntax='Packages/QSP/qsp.sublime-syntax')
		self.window.focus_view(new_view)
		self.window.run_command('qsp_new_game_head')

class QspInvalidInput(sublime_plugin.EventListener):
	def on_modified(self, view):
		if view.syntax() is None or view.syntax().name != 'QSP':
			return None
		begin = view.sel()[0].begin()
		end = view.sel()[0].end()
		sr_locname = view.expand_to_scope(begin, 'meta.start_location.qsp')
		sr_lblname = view.expand_to_scope(begin, 'entity.name.qlabel.qsp')
		if begin == end and sr_locname is not None:
			input_text = view.substr(sr_locname)
			all_locations = QspWorkspace.get_all_qsplocs(view) # list
			loc_names, loc_regions, loc_paths = zip(*all_locations) 
			if not input_text in loc_names:
				return None
			i = loc_names.index(input_text)
			region = sublime.Region(loc_regions[i][0], loc_regions[i][1])
			current_qsps, project_folder = QspWorkspace.get_main_pathes(view)
			if not (current_qsps is None or project_folder is None):
				qsps_relpath = os.path.relpath(current_qsps, project_folder)
			else:
				qsps_relpath = ''
			if sr_locname.intersects(region) and qsps_relpath == loc_paths[i]:
				return None
			content = "<style>.location_name {color:#ff8888;font-weight:bold;}</style>Локация с именем <span class='location_name'>%s</span> уже существует в проекте." % input_text
			view.show_popup(content, flags=32+8, location=begin+5, max_width=250)
		if begin == end and sr_lblname is not None:
			input_text = view.substr(sr_lblname)
			qsp_labels = QspWorkspace.get_qsplabels_from_symbols(view, exclude_inputting=sr_lblname)
			if input_text in qsp_labels:
				content = "<style>.lbl_name {color:#99ff55;font-weight:bold;}</style>Метка с именем <span class='lbl_name'>%s</span> уже есть в этом файле." % input_text
				view.show_popup(content, flags=sublime.HTML, location=-1, max_width=250)

class QspTips(sublime_plugin.EventListener):

	def on_selection_modified(self, view):
		""" Show tips in statusbar """
		if view.syntax() is not None and view.syntax().name == 'QSP':
			word_coords = view.word(view.sel()[0].begin()) # Region
			word = view.substr(word_coords).lower() # str
			p = word_coords.begin()-1 # int (Point)
			pref = (view.substr(word_coords.begin()-1) if p > -1 else '') # str
			keywords = CMD_TEMPLATES.keys()
			if pref == '*' and ('*' + word in keywords):
				word = '*' + word
				match = re.match(r'^\*\w+\b$', word)
			elif pref == '$' and ('$' + word in keywords):
				word = '$' + word
				match = re.match(r'^\$\w+\b$', word)
			else:
				match = re.match(r'^\w+\b$', word)
			if (match is not None) and (word in keywords):
				sublime.status_message(CMD_TEMPLATES[word])

# class QspAddLighting(sublime_plugin.EventListener):

# 	def on_selection_modified(self, view):
# 		""" HighLight- """
# 		global QSP_TRYER
# 		if view.syntax() is not None and view.syntax().name == 'QSP':
# 			if QSP_TRYER:
# 				user_variable = r'\$?[A-Za-zА-Яа-я_][\w\.]*'
# 				regions = view.find_all(user_variable, 2)
# 				variables = set()
# 				for r in regions:
# 					if view.match_selector(r.begin(), 'meta.user-variables.qsp'):
# 						variables.add(view.substr(r))
# 				print(list(variables))
# 				QSP_TRYER = False

class QspAutocomplete(sublime_plugin.EventListener):
	""" Autocomplete and helptips """

	def on_query_completions(self, view, prefix, locations):
		""" append completions in editor """
		if view.syntax() is None or view.syntax().name != 'QSP':
			return []
		# extract all datas
		all_locations = QspWorkspace.get_all_qsplocs(view) # -> list of locations
		# if syntshugarfunc
		if view.match_selector(locations[0]-1, 'variable.function.qsp'):
			qsp_locations = []
			prefix = prefix.lower()
			for loc_name, loc_region, loc_path in all_locations:
				if loc_name.lower().startswith(prefix):
					d = sublime.CompletionItem(
						loc_name,
						annotation="Локация",
						completion=loc_name,
						completion_format=sublime.COMPLETION_FORMAT_TEXT,
						kind=sublime.KIND_FUNCTION
					)
					qsp_locations.append(d)
			return (qsp_locations, 24)
		# if calable operator call location
		elif view.match_selector(locations[0]-1, 'callable_locs.qsp'):
			qsp_locations = []
			scope_region = view.expand_to_scope(locations[0]-1, 'callable_locs.qsp')
			input_text = view.substr(scope_region)
			for loc_name, loc_region, loc_path in all_locations:
				if loc_name.lower().startswith(input_text[1:-1]):
					d = sublime.CompletionItem(
						loc_name,
						annotation="Локация",
						completion=loc_name,
						completion_format=sublime.COMPLETION_FORMAT_TEXT,
						kind=sublime.KIND_FUNCTION
					)
					qsp_locations.append(d)
			return (qsp_locations, 24)
		elif view.match_selector(locations[0]-1, 'label_to_jump.qsp'):
			all_labels = QspWorkspace.get_qsplabels_from_symbols(view)
			scope_region = view.expand_to_scope(locations[0]-1, 'label_to_jump.qsp')
			input_text = view.substr(scope_region)
			qsp_labels = []
			for qsp_lb in all_labels:
				if qsp_lb.lower().startswith(input_text[1:-1]):
					d = sublime.CompletionItem(
						qsp_lb,
						annotation="Метка",
						completion=qsp_lb,
						completion_format=sublime.COMPLETION_FORMAT_TEXT,
						kind=sublime.KIND_MARKUP
					)
					qsp_labels.append(d)
			return (qsp_labels, 24)
		else:
			return []

class QspWorkspaceLoader(sublime_plugin.EventListener):
	""" Manage a qsp-workspace in ram and in files """

	commands_log = {'current': '', 'last': ''}

	def _extract_qsp_ws(self):
		""" extract ws from file if file is exist, and load in ram """
		argv = sublime.active_window().extract_variables()
		project_folder = (argv['folder'] if 'folder' in argv else None)
		if project_folder is None:
			return None
		qws = QSP_WORKSPACES[project_folder] = QspWorkspace()
		if os.path.isfile(os.path.join(project_folder, 'qsp-project-workspace.json')):
			# если файл существует, извлекаем из файла
			qws.extract_from_file(project_folder=project_folder)

	def _save_qsp_ws(self, view):
		""" save ws from ram in file """
		current_qsps = view.file_name()
		if current_qsps is None:
			return None
		argv = sublime.active_window().extract_variables()
		project_folder = (argv['folder'] if 'folder' in argv else None)
		if project_folder is None:
			return None
		if project_folder in QSP_WORKSPACES:
			# if ws exist in dict of wss
			qsp_ws = QSP_WORKSPACES[project_folder]
		else:
			# if ws dont exist in dict of wss
			qsp_ws = QSP_WORKSPACES[project_folder] = QspWorkspace()
		qsp_ws.refresh_locs_from_symbols(view)
		qsp_ws.save_to_file(project_folder)

	def _after_replace(self, command_name:str = ''):
		print('commands_log', self.commands_log)
		self.commands_log['last'], self.commands_log['current'] = self.commands_log['current'], command_name
		if self.commands_log['last'] in ('delete_file', 'rename_path'):
			project_folder = QspWorkspace.get_cur_pf()
			if project_folder is None or not project_folder in QSP_WORKSPACES:
				return None
			qsp_ws = QSP_WORKSPACES[project_folder]
			sublime.set_timeout_async(lambda: qsp_ws.refresh_files_paths(), 180)

	def on_close(self, view):
		if view.syntax() is not None and view.syntax().name == 'QSP':
			self._save_qsp_ws(view)

	def on_pre_save(self, view):
		if view.syntax() is not None and view.syntax().name == 'QSP':
			self._save_qsp_ws(view)

	def on_init(self, views):
		self._extract_qsp_ws()

	def on_load_project(self, window:sublime.Window) -> None:
		self._extract_qsp_ws()
