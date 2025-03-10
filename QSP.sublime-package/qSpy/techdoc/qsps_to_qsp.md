# Конвертер `qsps_to_qsp.py`

> формат TXT2GAM и qsps — это одно и то же. Это текстовые файлы с особым форматом записи QSP-кода.

Скрипт основан на JS-скрипте Werewolf'а для конвертирования текстовых файлов формата qsps в файлы QSP: [https://codepen.io/srg-kostyrko/full/QWqdwxv](https://codepen.io/srg-kostyrko/full/QWqdwxv)

## Конвертирование файла

Конвертирование одного файла qsps в QSP делается следующим образом:

1. Создаём экземпляр класса `NewQspsFile`, не указывая параметров.
2. Для созданного объекта вызываем метод `convert_file()`, указав в качестве параметра путь к конвертируемому файлу qsps.

Пример:

Сконвертирует в QSP-формат файл `tooloz.qsps`:

```python
qsps_to_qsp = NewQspsFile()
qsps_to_qsp.convert_file('tooloz.qsps')
```

Далее можно работать с данными в экземпляре класса, используя другие методы.

### Результат работы

Рядом с исходным файлом создаётся одноимённый QSP-файл. Первые три строки этого файла выглядят примерно так:

```qsp
QSPGAME
qsps_to_qsp SublimeText QSP Package
Ij
```

Подробнее о том, что значат эти строки можно почитать в [описании формата QSP](https://github.com/QSPFoundation/qsp/blob/master/help/gam_desc.txt).

## Работа с экземпляром класса NewQspsFile

Вам может потребоваться более гибкая работа при конвертировании игры, например, сконвертировать одну локацию, или исключить несколько. Для этого в конвертере предусмотрены различные методы обработки данных.

В момент создания экземпляр класса пуст и не хранит никаких данных.

### Создание экземпляра класса

```python
qsps_to_qsp = NewQspsFile()
```

### .convert_file()

Конвертирует указанный файл в файл QSP.

```python
.convert_file(input_file:str) -> output_file:str
```

Параметры:

- `input_file` — путь к конвертируемому файлу (обязательный).

Возвращает:

- путь к полученному файлу.

### .read_from_file()

Считывает данные с указанного файла и записывает в экземпляр класса.

```python
.read_from_file(input_file:str=None) -> None
```

Параметры:

- `input_file` — путь к считываемому файлу. Если указан, на основе этого пути [устанавливаются параметры различных путей](#.set_input_file()) в экземпляре класса. Если не указан, данные считываются из файла, который уже был прописан в поле экземпляра класса.

### .save_to_file()

Записывает данные сконвертированной игры из экземпляра класса в указанный файл.

```python
.save_to_file(output_file:str=None) -> None
```

Параметры:

- `output_file` — путь к записываемому файлу. Если не указан, используется путь к выходному файлу, прописанный в экземпляре класса.

### .set_input_file()

Устанавливает в экземпляре класса различные пути: путь к исходному файлу, путь к записываемому файлу, путь к выходной папке и чистое имя файла без расширения.

```python
.set_input_file(input_file:str) -> None
```

Параметры:

- `input_file` — путь к исходному файлу. Обязателен.

### .set_file_source()

Добавляет в экземпляр класса исходные данные для конвертирования.

```python
.set_file_source(file_Strings:list) -> None
```

Параметры:

- `file_strings` — данные для конвертирования в формате qsps. Например, считанные другими методами из qsps-файла Обязателен. Данные представляют собой список строк обычного текстового файла.

### .split_to_locations()

Разделяет исходные данные формата qsps на отдельные [локации](#Работа%20с%20экземпляром%20класса%20NewQspLocation).

```python
.split_qsp() -> None
```

### .append_location()

Добавляет локацию в список локаций.

```python
.append_location(location:NewQspLocation) -> None
```

Параметры:

- `location` — локация в виде экземпляра класса [NewQspLocation](#Работа%20с%20экземпляром%20класса%20NewQspLocation).

### .to_qsp()

Конвертирует все собранные на предыдущих этапах данные в QSP-формат.

```python
.to_qsp() -> None
```

Функция ничего не возвращает, однако сконвертированные строки помещаются в поле `converted_strings` экземпляра класса.

### .get_qsplocs()

Возвращает список списков, состоящих из названия локации и региона в файле, где это название прописано.

```python
.get_qsplocs() -> list[location_name:str, locname_region:tuple]
```

Возвращает:

- Список списков, первый элемент в которых — имя [локации](#Работа%20с%20экземпляром%20класса%20NewQspLocation), а второй элемент — регион в файле, в котором находится это имя.

### .parse_string()

Парсит открытие строк в коде локаций, или в других местах, чтобы своевременно переключать режимы и допускать внутри строк паттерны токенов, размечающих содержимое игры.  Статический метод.

```python
.parse_string(qsps_line:str, mode:dict) -> None
```

Параметры:

- `qsps_line` — строка к обработке.
- `mode` — [словарь режимов](#словарь%20режимов).

Результат распарсивания строк записывается в словарь режимов `mode`.

### .encode_qsps_line()

Кодирует qsps-строку. Статический метод.

```python
.encode_qsps_line(qsps_line:str) -> str
```

Параметры:

- `qsps_line` — строка к обработке.

Возвращает:

-  зашифрованная строка, необходимая для записи в файл QSP.

### .encode_char()

Кодирует qsps-строку. Статический метод.

```python
.encode_char(point:str) -> str
```

Параметры:

- `point` — строка из одного символа.

Возвращает:

-  новый символ после шифровки.

## Работа с экземпляром класса NewQspLocation

Экземпляр класса `NewQspLocation` (далее все экземпляры этого класса будут называться просто локациями) представляет собой отдельный объект для хранения данных локации QSP. За счёт выделения отдельного класса получилось инкапсулировать методы, применимые конкретно к локациям QSP, а не реализовывать их в основном объекте модуля.

### Создание экземпляра класса

При создании локации указывается её имя, а так же можно сразу передать код локации в виде списка строк qsps.

Например, вот так будет создана локация с именем `start`. Все прочие поля локации будут пусты.

```python
qsp_loc = NewQspLocation('start')
```

### .change_name()

Позволяет сменить имя локации.

```python
.change_name(new_name:str) -> None
```

Параметры:

- `new_name` — новое название локации.

### .change_region()

Позволяет изменить [*регион*](#Регион) местоположения названия локации в файле.

```python
.change_region(new_region:tuple) -> None
```

Параметры:

- `new_region` — новый регион.

### .change_code()

Позволяет заменить весь код локации.

```python
.change_code(new_code:list) -> None
```

Параметры:

- `new_code` — новый код локации в виде списка строк qsps.

### .add_code_line()

Добавляет к коду локации строку.

```python
.add_code_line(code_line:str) -> None
```

Параметры:

- `code_line` — добавляемая строка кода QSP (qsps строка).

### .extract_base()

Извлекает из кода локации строки кода, содержащие базовое описание локации и её базовые действия.

```python
.extract_base() -> None
```

### .split_base()

Из строк кода, содержащих базовое описание и базовые действия локации, извлекает непосредственно базовое описание и базовые действия.

```python
.split_base() -> None
```

### .encode()

Кодирует данные из локации в строки, подходящие для записи формата QSP-игры. Не возвращает результат. Результат помещается в специальное поле локации.

```python
.encode() -> None
```

### .get_qsp()

Извлекает закодированный в формате QSP-файла полный текст локации.

```python
.get_qsp() -> list
```

Возвращает:

- список зашифрованных строк в формате подходящем для записи в QSP-файл.

### Различные поля

- `name` - название локации
- `name_region` - регион в файле, в котором объявлено название локации.
- `code` - список строк кода локации (поле локации "выполнить при посещении").
- `base_code` - временный список строк кода, объявляющих базовое описание и базовые действия локации.
- `base_description` - общая строка с базовым описанием локации, извлечённая из `base_code`.
- `base_actions` - список [базовых действий](#Базовое%20действие) локации.


## Структуры данных, использующиеся в конвертере

### Регион

Регион — это некая область в текстовом файле. Обозначается двумя целыми числами: начало и конец региона, — каждое число является просто количеством символов от начала файла.

Технически представляет собой кортеж из двух целочисленных элементов. Пример:

```python
region = (232, 239) # локация с именем "[start]"
```

### Базовое действие

```python
{
	'image': '', # путь к изображению действия
	'name': '', # название действия
	'code': [] # список строк кода действия
 }
```

### словарь режимов

Это словарь, в котором перечислены режимы, необходимые для распарсивания текущего исходного кода.

```python
{
	'open-string': '', # содержит символы открытия строки по порядку кавычки, апострофы, фигурные скобки
	
}
```

## Конвертирование без исходного файла

Такое конвертирование может использоваться, когда список строк формируется где-то вне модуля. Например, мы считали qsps-файл, обработали его препроцессором, теперь нам нужно конвертировать его и сохранить:

```python
# qsps_src_lines = [...]
# output_path = '...'
qsps_to_qsp = NewQspsFile()
qsps_to_qsp.set_file_source(qsps_src_lines)
qsps_to_qsp.split_to_locations()
qsps_to_qsp.to_qsp()
qsps_to_qsp.save_to_file(output_path)
```