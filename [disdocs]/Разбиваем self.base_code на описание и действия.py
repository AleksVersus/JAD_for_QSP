# Разбиваем self.base_code на описание и действия
		self.base_description = []
		self.base_actions = []

		# Вспомогательная функция для пропуска пробельных символов в строке
		def skip_whitespace(text, pos):
			while pos < len(text) and text[pos].isspace():
				pos += 1
			return pos

		# Вспомогательная функция для парсинга строки в кавычках (поддерживает многострочные аргументы)
		def parse_quoted(lines, idx, pos, quote):
			"""Парсит строку, заключённую в кавычки quote, возможно, с переносами строк."""
			result = ""
			while True:
				line = lines[idx]
				end = line.find(quote, pos)
				if end != -1:
					result += line[pos:end]
					pos = end + 1
					return result, idx, pos
				else:
					# Добавляем всю оставшуюся часть строки и переход на новую строку
					result += line[pos:] + "\n"
					idx += 1
					if idx >= len(lines):
						# Если не найдено закрывающей кавычки, возвращаем накопленный результат
						return result, idx, 0
					pos = 0

		# Функция для парсинга команды. command_type может быть "p" или "act"
		def parse_command(command_type, lines, idx, pos):
			# Для оператора *p ожидается ровно один аргумент в кавычках
			if command_type == "p":
				if pos >= len(lines[idx]) or lines[idx][pos] not in "'\"":
					return None, idx, pos
				quote = lines[idx][pos]
				pos += 1
				arg, idx, pos = parse_quoted(lines, idx, pos, quote)
				return {"cmd": "p", "args": [arg]}, idx, pos
			# Для оператора act ожидается один или два аргумента в кавычках, затем обязательно двоеточие
			elif command_type == "act":
				# Парсим первый аргумент
				if pos >= len(lines[idx]) or lines[idx][pos] not in "'\"":
					return None, idx, pos
				quote = lines[idx][pos]
				pos += 1
				arg1, idx, pos = parse_quoted(lines, idx, pos, quote)
				args = [arg1]
				# Пропускаем пробелы после первого аргумента
				pos = skip_whitespace(lines[idx], pos)
				# Проверяем разделитель для второго аргумента (если есть)
				if pos < len(lines[idx]) and lines[idx][pos] == ',':
					pos += 1
					pos = skip_whitespace(lines[idx], pos)
					if pos >= len(lines[idx]) or lines[idx][pos] not in "'\"":
						return None, idx, pos
					quote = lines[idx][pos]
					pos += 1
					arg2, idx, pos = parse_quoted(lines, idx, pos, quote)
					args.append(arg2)
					pos = skip_whitespace(lines[idx], pos)
				# После аргументов обязательно должен идти двоеточие
				if pos >= len(lines[idx]) or lines[idx][pos] != ':':
					return None, idx, pos
				pos += 1
				# Дополнительные символы после двоеточия недопустимы
				pos = skip_whitespace(lines[idx], pos)
				if pos < len(lines[idx]):
					return None, idx, pos
				return {"cmd": "act", "args": args}, idx, pos
			return None, idx, pos

		i = 0
		while i < len(self.base_code):
			line = self.base_code[i]
			stripped = line.lstrip()
			# Проверяем наличие команды *p (без учета регистра)
			if stripped.lower().startswith("*p"):
				# Определяем позицию после оператора *p
				op_len = 2
				pos = len(line) - len(stripped) + op_len
				pos = skip_whitespace(line, pos)
				cmd, new_i, new_pos = parse_command("p", self.base_code, i, pos)
				if cmd:
					self.base_actions.append(cmd)
					# Если команда распарсена в рамках одной строки, переходим к следующей; иначе - продолжаем с новой строки
					i = new_i if new_i != i else i + 1
				else:
					self.base_description.append(line)
					i += 1
			# Проверяем наличие команды act (без учета регистра)
			elif stripped.lower().startswith("act"):
				op_len = 3
				pos = len(line) - len(stripped) + op_len
				pos = skip_whitespace(line, pos)
				cmd, new_i, new_pos = parse_command("act", self.base_code, i, pos)
				if cmd:
					self.base_actions.append(cmd)
					i = new_i if new_i != i else i + 1
				else:
					self.base_description.append(line)
					i += 1
			else:
				# Если строка не начинается с допустимой команды, добавляем ее в описание
				self.base_description.append(line)
				i += 1