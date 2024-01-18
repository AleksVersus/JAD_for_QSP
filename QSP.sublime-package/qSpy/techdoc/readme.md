# qSpy

Изначально это был набор вспомогательных скриптов, но число этих скриптов разрослось, так что пришлось объединить их в один общий пакет модулей.

**Внимание!!!** Все скрипты данного пакета запускаются прямо из Sublime Text и работают как составные части плагина. Читайте [полную инструкцию](https://github.com/AleksVersus/JAD_for_QSP/blob/master/README.md).

## Модули qSpy:

* `builder.py` — основной модуль билдера с единственным классом. Нельзя использовать, как самостоятельный скрипт. Зависит от `function.py` и `qsps_to_qsp.py`.
* `function.py` — набор необходимых для билдера функций. Практически бесполезен, как самостоятельный модуль.
* `pp.py` — набор функций, выполняющих роль препроцессора. Может запускаться отдельно от билдера для препроцессинга отдельных файлов.

* `qsps_to_qsp.py` — конвертер, конвертирующий qsps-файл в QSP-файл игры. Может использоваться самостоятельно.
* `qsp_to_qsps.py` — скрипт конвертера, конвертирующий QSP-файл игры в qsps-файл (файл формата TXT2GAM). Может использоваться самостоятельно.
* `qsp_splitter.py` — скрипт разделителя. Использует скрипт конвертера в случае, если должен обработать QSP-файл игры. Можно использовать самостоятельно для разделения qsps-файлов.
* `main_cs.py` — конвертер-разделитель для больших проектов. Данный скрипт упрощает работу с проектами, уже разбитыми на несколько QSP-файлов (модулей). Позволяет просканировать текущую папку на наличие в ней QSP-файлов, сконвертировать все найденные файлы в qsps-формат, а затем разбить на отдельные файлы локаций.

## Самостоятельное тестирование скриптов

### Простой запуск конвертера-разделителя. Скрипт `main_cs.py`

Чтобы сконвертировать в наборы файлов локаций все составляющие игры (основной QSP-файл и модули):

* разместите составляющие файлы и их одноймённые файлы `.qproj` в папке со скриптом
* запустите скрипт

Простой запуск выполняется с помощью скрипта `main_cs.py`. Данный скрипт проводит работу в двух режимах:

1. Поиск и конвертация всех QSP-файлов в папке. Скрипт:
	* отыщет все QSP-файлы (файлы с расширением `.qsp`) и все qsps-файлы (файлы с расширением `.qsps`) в указанной папке (по умолчанию текущая);
	* QSP-файлы сконвертирует в qsps;
	* qsps-файлы (ранее созданные и новые) разделит на отдельные файлы локаций.
	* В результате на каждый QSP-файл или qsps-файл будет создана одноимённая папка, в которой будут размещены подпапки и файлы локаций согласно структуре файла `.qproj`. Если соответствующий файл `.qproj` не найден, все локации будут помещены в одну папку.
2. Конвертирование `game.txt`. Данный режим запускается, если не удалось найти ни одного QSP- и qsps-файла при запуске первого режима.
	* Скрипт попытается найти файл `game.txt` в указанной папке.
	* Если файл будет найден, будет создана папка `export_game`, в которую попадут папки и файлы локаций согласно структуре файла `game.qproj`.
	* Если файл не будет найден, скрипт завершит работу выводом надписи об ошибке.

Чтобы обработать файлы в произвольной папке, не перемещая скрипт, измените значение переменной `folder_path` в функции `main()` скрипта, указав путь к нужной папке.

### Запуск конвертера-разделителя для отдельного файла

Вы можете сконвертировать любой QSP-файл в формат qsps и разбить на отдельный файлы локаций, используя скрипт `qsp_splitter.py`. Для этого в функции `main()` впишите в словарь `arg`s такую пару ключ-значение:

```py
args = {"game-file": "file_path"}
```

Здесь вместо `file_path` должен быть указан путь до QSP-файла, который вы хотите сконвертировать и разбить на локации.

Если вам нужно разбить на локации уже готовый qsps-файл, укажите путь до него, как значение для ключа "qsps-file" в том же словаре `args`:

```py
args = {"qsps-file": "file_path"}
```

### Запуск конвертера для отдельного QSP-файла

Если необходимо сконвертировать отдельный QSP-файл в формат qsps без разделения, воспользуйтесь скриптом `qsp_to_qsps.py`. Для этого в функции `main()` исправьте значение в словаре `args`, соответствующее ключу "`game-file`" на путь до файла, который хотите сконвертировать. И запустите скрипт.

### Запуск конвертера для отдельного qsps-файла

Если необходимо сконвертировать отдельный qsps-файл в QSP-файл без запуска билдера, воспользуйтесь скриптом `qsps_to_qsp.py`. Для этого в функции `main()` исправьте значение переменной `input_file` на путь до файла, который хотите сконвертировать. И запустите скрипт.

Если необходимо сконвертировать отдельный QSP-файл в формат qsps без разделения, воспользуйтесь скриптом `qsp_to_qsps.py`. Для этого в функции `main()` исправьте значение в словаре `args`, соответствующее ключу "`game-file`" на путь до файла, который хотите сконвертировать. И запустите скрипт.

### Запуск препроцессора для отдельного qsps-файла

Если необходимо обработать препроцессором qsps-файл, не запуская билдер, воспользуйтесь скриптом `pp.py`. Для этого в функции `main()` замените значение переменной `file` на путь к qsps-файлу, который хотите обработать.

### Требования к qsps-файлам

Если необходимо разбить на части не QSP-файл, а qsps, такой файл должен быть экспортированным из Quest Generator в формате qsps (TXT2GAM), или получен применением конвертера `qsp_to_qsps.py`.

* Кодировка UTF-8. Либо UTF-16 с BOM-символом в начале.
* Начало локации должно записываться как:
```qsp
# название_локации
```
* Конец локации обязательно должен записываться как
```qsp
--- название_локации ---------------------------------
```
