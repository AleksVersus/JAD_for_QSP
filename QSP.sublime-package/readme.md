# Пакет QSP

Включает в себя:
* `Default.sublime-keymap` - файл настройки сочетаний клавиш при работе с QSP-файлом
* `Indentation Rules.tmPreferences` - файл настройки поведения отступов
* `Location in Goto-List.tmPreferences` - файл настройки распознавания локаций в проекте
* `Markup in Goto-List.tmPreferences` - файл настройки распознавания меток на локации
* `QSP.sublime-build` - файл настройки build-system для сборки файлов `.qsp`.
* `qsp.sublime-syntax` - файл со схемой подсветки синтаксиса QSP
* `qsp_locations.sublime-syntax` - дополнительный файл со схемой подсветки синтаксиса QSP, предназначенный для встраивания подсветки QSP в схемы подсветки других языков.
* `syntax_test_qsp.qsps` - файл с образцом синтаксиса QSP для теста подсветки (не билдится сублаймом).

1. Отредактируйте файлы "`Default.sublime-keymap`" и "`QSP.sublime-build`" (подробнее читайте на [https://github.com/AleksVersus/JAD_for_QSP](https://github.com/AleksVersus/JAD_for_QSP));
2. Упакуйте всё содержимое данной папки в zip-архив и переименуйте его так, чтобы он назывался "`QSP.sublime-package`";
3. Скопируйте файл "`QSP.sublime-package`" в папку Packages установленного у вас Sublime Text (например, у меня она расположена по пути "`C:\Program Files\Sublime Text\Packages`").
4. Перезагрузите Sublime Text - подсветка, сниппеты и билдер будут работать.