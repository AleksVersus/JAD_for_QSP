# Пакет QSP

**Включает в себя:**

* `qSpy` и `QSP.py` - python-скрипты, реализующие билдер qsp-игр в виде плагина для ST.
* `Snippets` - папка со стандартными сниппетами (фрагментами кода) для QSP.
* `.python-version` - версия встроенного интерпретатора python, в которой будет запускаться плагин
* `Comment Intendation.tmPreferences` - настройка поведения для вставки комментариев.
* `Default.sublime-keymap` - файл настройки сочетаний клавиш при работе с QSP-файлом
* `Indentation Rules.tmPreferences` - файл настройки поведения отступов
* `Location in Goto-List.tmPreferences` - файл настройки распознавания локаций в проекте
* `Markup in Goto-List.tmPreferences` - файл настройки распознавания меток на локации
* `QSP.sublime-build` - файл настройки build-system для сборки файлов `.qsp`.
* `qsp.sublime-syntax` - файл со схемой подсветки синтаксиса QSP
* `qsp_locations.sublime-syntax` - дополнительный файл со схемой подсветки синтаксиса QSP, предназначенный для встраивания подсветки QSP в схемы подсветки других языков.
* `syntax_test_qsp.qsps` - файл с образцом синтаксиса QSP для теста подсветки (не билдится сублаймом).

**Для установки пакета:**

1. Скопируйте файл "`QSP.sublime-package`" в папку Packages установленного у вас Sublime Text (например, у меня она расположена по пути "`C:\Program Files\Sublime Text\Packages`").
2. Перезагрузите Sublime Text - подсветка, сниппеты и билдер будут работать.