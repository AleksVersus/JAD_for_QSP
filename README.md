# JAD for QSP
JAD — joint application development

Или по-русски: совместная разработка приложений. В нашем случае **Joint QSP-Games Development**, только аббревиатура выходит некрасивая.)

Здесь я пытаюсь описать порядок совместной разработки QSP-игр и выбранные мной инструменты.

## Содержание

*	[Разработка QSP-игр в Sublime Text](#Разработка-QSP-игр-в-Sublime-Text)
	*	[Выбор редактора](#Выбор-редактора)
	*	[Порядок работы с проектом](#Порядок-работы-с-проектом)
	*	[project.json](#projectjson)
		*	[Пути](#Пути)
	*	[QSP-Builder for Sublime Text](#QSP-Builder-for-Sublime-Text)
		*	[Установка QBST](#Установка-QBST)
		*	[Порядок сборки и запуска](#Порядок-сборки-и-запуска)
		*	[Ошибки](#Ошибки)
		*	[Пример проекта](#Пример-проекта)
*	[Подсветка синтаксиса QSP](#Подсветка-синтаксиса-QSP)
*	[Совместная разработка и контроль версий](#Совместная-разработка-и-контроль-версий)
	*	[Контроль версий](#Контроль-версий)
		*	[Sublime Merge](#Sublime-Merge)
	*	[Совместная разработка](#Совместная-разработка)
	*	[Заключение](#Заключение)
*	[P.S.:](#PS)

## Разработка QSP-игр в Sublime Text

### Выбор редактора, или Почему Sublime Text?

Всем новичкам в разработке игр на QSP я предлагаю начинать с Quest Generator, так как он удобен, прост и интуитивно понятен. Пишешь локации, запускаешь игру нажатием на кнопку - тестируешь.

Однако со временем выявляются разного рода недостатки, присущие Quest Generator'у. И эти недостатки подталкивают нас к поиску более удобного и функционального редактора.

В идеале нам нужен редактор, который на лету проверяет очевидные ошибки, из которого можно запустить игру прямо в плеере, и который обеспечит нам контроль версий и работу с репозиторием, например, на гитхабе.

По-идее нам подходит **VS Code**, так как это очень удобное IDE с уже встроенными инструментами для взаимодействия с системами контроля версий (по нажатию пары кнопок можно делать коммиты и отправлять их в репозиторий), но пока не доделано [расширение Псевдопода](http://qsp.su/index.php?option=com_agora&task=topic&id=1286&Itemid=57), лично для меня **VS Code** остаётся не очень удобным редактором, и я использую его разве что для проверки ошибок в различных играх.

Ещё на заре появления QSP была создана утилита [TXT2GAM](http://qsp.su/index.php?option=com_content&task=view&id=52&Itemid=56), которая позволяет разрабатывать игру в виде текстового файла (исходника) в любом текстовом редакторе, а потом конвертировать исходник в готовый файл игры. Но, к сожалению, мало какой текстовый редактор мог похвастаться адекватной [подсветкой кода QSP](http://qsp.su/index.php?option=com_agora&task=topic&id=686&Itemid=57).

Я решил остановиться на **Sublime Text**, поскольку этот редактор позволяет даже мне, не особо шарящему в программировании, написать собственную подсветку синтаксиса, имеет выход на консоль и собственный Python-интерпретатор. К тому же я давно пользуюсь данным редактором для обычной писательской деятельности, и настолько привык к нему, что уже не представляю, может ли быть что-то удобнее.

Ко всему прочему я возобновил изучение Python, одно наложилось на другое, и всё это в итоге вылилось в разработку специального скрипта, который собирает из разрозненных файлов в формате TXT2GAM обычный файл игры на QSP с расширением "`.qsp`". Также я переработал старую подсветку QSP для **Sublime Text** и теперь она гораздо более адекватно работает с файлами формата TXT2GAM.

Если вы не знаете, как пишутся игры на QSP в формате TXT2GAM, ознакомьтесь с уроками от ELMORTEM: http://qsp.su/index.php?option=com_content&view=article&id=91&Itemid=56

Работа в **Sublime Text** по сравнению с **Quest Generator** имеет ряд преимуществ:

* **Контроль версий.** Поскольку все части игры хранятся в виде текстовых файлов (исходного кода), они легко обрабатываются системами контроля версий, например GIT. Таким образом, вы можете проследить все этапы создания вашей игры, и быстрее находить ошибки.
* **Совместная разработка.** Вы можете организовать общий репозиторий, например на GitHub, и разрабатывать игру командой, при этом можно легко отследить, кто и какие изменения вносит в проект.
* **Удобство модульной разработки.** Вы можете одновременно в одной программе работать над всеми модулями вашей игры, или открывать для каждого модуля своё окно, или пользоваться любыми иными возможностями **Sublime Text**, а затем собрать и запустить игру, нажав всего одну комбинацию клавиш. QBST (см. раздел [**QSP-Builder for Sublime Text**](#QSP-Builder-for-Sublime-Text)) соберёт все нужные вам файлы "`.qsp`" и запустит игру в плеере по нажатию пары клавиш.
* **Один редактор - много плееров.** В специальном [файле проекта](#projectjson) можно для каждой игры указать собственный плеер. Таким образом, одну игру вы можете разрабатывать например для **qSpider**, одну для **Quest Navigator**, а другую для **классики**. И вам не придётся ставить себе три **Quest Generator** с разными настройками для плееров.
* **Sublime Text.** **Sublime Text** умеет подсвечивать HTML, JavaScript и CSS, что очень сильно облегчает разработку игр для **Quest Navigator** и **qSpider**. Если вам сильно не хватало проверки орфографии в **QGen**, то здесь вы [можете себе её сделать](https://devmag.ru/sublime-text-3-spellcheck/). Поиск и замена лишь по определённым файлам и папкам (а значит и локациям)? В **Sublime Text** есть и это. Сложно придумать, что умеет **QGen** и не умеет **Sublime Text** — гораздо проще придумать, что умеет **ST** и не умеет **Quest Generator**.

### QSP-Builder for Sublime Text

QSP-Builder for Sublime Text (далее QBST, билдер) — это python-скрипт, который:

1. собирает из разрозненных файлов формата TXT2GAM файл игры в формате TXT2GAM;
2. конвертирует полученный файл в файл игры в формате "`.qsp`" (QSP-файл)
3. запускает указанный файл игры в плеер QSP

QBST принимает следующие аргументы, записанные в любом порядке и количестве:

`--b`, `--build`, `--buildandrun`, `--br` — данные аргументы разрешают непосредственно билд QSP-файла скрипту.

`--r`, `--run`, `--buildandrun`, `--br` — данные аргументы разрешают запуск QSP-файла в плеере.

...		Если ни один из вышеуказанных аргументов не указан, считается, что был передан `--br`.

`"file.qsps"` — название любого файла, от которого высчитывается расположение "`project.json`".

Поскольку скрипт запускается горячими клавишами, передаваемые ему параметры предопределены.

Возникающие ошибки для удобства помещаются в файл "`errors.log`", который может появиться либо рядом со скриптом, либо в папке с "`project.json`" в зависимости от того, в каком месте работы программы возникла ошибка.

К QBST прилагаются так же файлы "`QSP.sublime-build`" и "`QSP.sublime-keymap`", необходимые для установки и корректной работы QBST.

#### Установка QBST

1. Прежде всего у вас должен быть установлен Sublime Text, желательно Sublime Text 3. Скачать его можно отсюда https://www.sublimetext.com/3
2. Необходимо так же установить Python 3, если он до сих пор не установлен. Конечно, Sublime Text 3 включает собственный интерепретатор python, однако рекомендую скачать и установить полную версию с официального сайта https://www.python.org/downloads/ (Запишите путь к интерпретатору python, это понадобится нам в дальнейшем. Например, у меня Python расположен по этому адресу: "`C:\Program Files\Python39\python.exe`")
3. Теперь нужно скопировать файлы "`main.py`" и "`function.py`" из папки "`QBST`" в какую-нибудь отдельную папку. Я бы предложил скопировать их куда-нибудь поближе к плееру QSP. Например, у меня установлен Quest Navigator по адресу "`C:\Program Files (x86)\QSP\Quest Navigator\QuestNavigator.exe`", поэтому я создаю в папке "`C:\Program Files (x86)\QSP`" вложенную папку "`Builder`" и копирую туда файлы QBST (Точно так же запишите путь до файла "`main.py`", у меня он выглядит так: "`C:\Program Files (x86)\QSP\Builder\main.py`").
4. Следующее, что нужно сделать, это создать систему сборки QSP-файлов. Собственно, она уже создана, это файл "`QSP.sublime-build`". Вот как его установить:
	* Откройте Sublime Text и найдите меню "Preferences", откройте его и щёлкните по пунтку "Browse Packages..."
	* В открывшейся папке "Packages" откройте папку "User" и скопируйте в неё файл "`QSP.sublime-build`"
	* Откройте файл "QSP.sublime-build" с помощью Sublime Text и отредактируйте строки, содержащие путь к интерпретатору Python, указав путь к установленному на вашем компьютере интерпретатору. Т.е. замените путь "`C:\\Program Files\\Python39\\python.exe`" на ваш. Не забывайте экранировать бэкслэш дублированием.
	* Отредактируйте строки, содержащие путь к QBST, указав путь к файлу "`main.py`". Т.е. замените путь "`С:\\Program Files (x86)\\QSP\\Builder\\main.py`" на ваш. Не забывайте экранировать бэкслэш дублированием. Сохраните файл "`QSP.sublime-build`" и закройте.
5. Осталось только прописать горячие клавиши для сборки и запуска файлов "`.qsp`". Делается это следующим образом:
	* Откройте файл "`QSP.sublime-keymap`" с помощью Sublime Text.
	* В Sublime Text, в меню "Preferences" нажмите пункт "Key Bindings", откроется окно с двумя вкладками. В левой вкладке будут сочетания клавиш по умолчанию ("Default (...).sublime-keymap - Default"), а в правой — сочетания клавиш, определённые пользователем, т.е. вами ("Default (...).sublime-keymap - User"). 
	* Если содержимое правой вкладки пусто, просто скопируйте туда всё содержимое файла "`QSP.sublime-keymap`". Если Вы уже определяли какие-либо сочетания клавиш, то знаете, что из файла "`QSP.sublime-keymap`" нужно скопировать содержимое самых внешних квадратных скобок.
	* Если вам не нравятся назначенные мной сочетания клавиш, вы можете их переписать, заменив `["ctrl+f5"]`, `["ctrl+alt+q"]` и `["ctrl+alt+s"]` на иные сочетания.
	* После редактирования сохраните файл "Default (...).sublime-keymap - User".
6. На всякий случай перезапустите Sublime Text. QBST должен работать.

#### Порядок работы с проектом

1. Проект организуется по папкам. В корневой папке проекта должен лежать файл "`project.json`", который и содержит в себе инструкции по сборке проекта. (см. раздел "**project.json**").
2. Все рабочие файлы проекта пишутся в формате TXT2GAM и сохраняются с расширениями "`.qsps`", "`.qsp-txt`" или "`.txt-qsp`", предпочтительно указывать первое расширение. В качестве исключения можно указывать иные расширения, но в таком случае необходимо будет указывать пути до конкретных файлов (см. раздел "**project.json**").
3. После редактирования и сохранения файлов можно выбрать один из режимов сборки:
	* "QSP - qsp-build" — собрать файлы согласно инструкции и сконвертировать в "`.qsp`"
	* "QSP - qsp-run" — запустить стартовый файл, указанный в проекте "`project.json`", в плеере.
	* "QSP" — собрать файлы согласно инструкции и запустить стартовый файл в плеере.

Для примера рассмотрим мой проект игры "*fantastic battles*", который я писал в Quest Generator.

В этом проекте пришлось разбить игру на отдельные модули для удобства разработки, и всего таких модулей получилось четыре:
* "`fb_v.0.2.qsp`" — основной файл игры, в котором подключаются все прочие файлы модулей
* "`intro.qsp`" — модуль вводных данных игры
* "`drive.qsp`" — основной движок игры
* "`bases.qsp`" — различные базы исходников для игры

Каждый из этих файлов может содержать множество локаций, поэтому для самих файлов ведутся файлы "`.qproj`", которые содержат псевдопапки. Например, в "`fb_v.0.2.qsp`" локации разбиты на псевдопапки:

-	-	"`[start]`" — стартовая локация без папки
-	"`системное меню`" — папка с локациями основного меню
	-	"`[1.0_game_start]`" — локация, запускающая игру
	-	"`[0.1_game_info]`" — локация с информацией об игре
-	"`локации места`" — папка локаций места, и собственно локации:
	-	"`[м:0]_общий_вид_локации_места`"
	-	"`[м:1]_дом`"
	-	"`[м:2]_улица`"
	-	"`место;стандартная_кухня`"
-	"`обязательные локации`" — папка стандартных локаций для этой игры
	-	"`[chest]`" — сундуки
	-	"`[death]`" — смерть
	-	"`[help]`" — помощь

Работая в редакторе типа Sublime Text, я могу не только разбить данный файл игры на отдельные файлы и разместить их по папкам, но каждую локацию писать в отдельном файле. Я могу создавать подпапки и т.д., а потом собирать те же четыре файла из разрозненных qsps-файлов.

В данном случае я бы выделил отдельную папку под каждый модуль, в том числе — под основной файл игры. Допустим так:

- "`[game]`" — папка с основным файлом игры
    - "`start.qsps`" — файл со стартовой локацией
    - "`системное меню`" — папка с локациями системного меню
        - "`sysmenu.qsps`" — обе локации системного меню в одном файле
    - "`локации места`" — папка для локаций мест, можно дополнить другими папками
        - "`стандартные места`" — папка для стандартных локаций мест
            - "`общий вид локации места.qsp-txt`" — файл с локацией "`[м:0]_общий_вид_локации_места`"
		- "`дом.qsps`" — файл с локацией "`[м:1]_дом`"
		- "`улица.qsps`" — файл с локацией "`[м:2]_улица`"
	- "`обязательные локации`" — папка с файлами обязательных локаций
		- "`chests.qsps`" — файл с локацией "`[chest]`"
		- "`death and help.qsps`" — файл с локациями "`[help]`" и "`[death]`"

Необходимо отметить, что бри сборке конечного файла из таких разрозненных файлов, к конечному файлу добавляются сначала локации из файлов, которые лежат в папках верхних уровней, затем файлы из папок нижних уровней. Таким образом локация из файла "`start.qsps`" окажется в самом верху списка локаций при создании файла "`.qsp`".

##### project.json

Пример с комментариями представлен в файле "`[disdocs]\example.json`".

Как видно из расширения, проект представляет собой JSON-файл. Это значит, что вся его структура состоит из JSON-объектов (в Python - это словари) и JSON-массивов (в Python - это списки). Немного более подробно о файлах формата JSON вы можете прочитать здесь: https://www.hostinger.ru/rukovodstva/chto-takoe-json

В данном случае корневым элементом является объект, в котором присутствуют четыре элемента:

```json
	"project":[]
	"start":"startgame.qsp"
	"converter":"C:\\Program Files\\QSP\\txt2gam.exe"
	"player":"C:\\Program Files\\QSP\\Quest Navigator\\QuestNavigator.exe"
```

Значением элемента "project" является массив однотипных объектов, в которых присутствуют следующие элементы:

```json
	"build":"exitfile.qsp"
	"top_location":"[start]"
	"files":[]
	"folders":[]
```

Элемент "build" содержит путь к конечному файлу "`.qsp`", который мы хотим получить.
Элемент "top_location" содержит название локации, которая должна идти самой первой в результирующем файле. В настоящее время не используется.
Элементы "files" и "folders" содержат массивы однотипных объектов. И в том и в другом случаем объекты содержат элементы "path", однако для "files" каждый элемент "path" содержит путь к конкретному файлу, из которого мы должны получить локации, а для "folders" каждый элемент "path" содержит путь к папке, и уже из этих папок выбираются файлы "`.qsps`", "`.qsp-txt`", "`.txt-qsp`".

Значением элемента "start" является путь к файлу, который необходимо запускать в плеере после билда. Это не обязательно должен быть один из собранных файлов, т.е. указать можно абсолютно любой файл "`.qsp`".
Значением элемента "converter" является путь к утилите, конвертирующей файлы формата TXT2GAM в файлы "`.qsp`".
Значением элемента "player" является путь к плееру, в котором необходимо запустить игру (например, после сборки).

Скачать утилиту TXT2GAM можно отсюда: http://qsp.su/index.php?option=com_content&task=view&id=52&Itemid=56

Различные плееры лежат здесь: http://qsp.su/index.php?option=com_content&view=article&id=64&Itemid=87 

##### Пути

Элементы "start","build" и "path" должны содержать абсолютные или относительные пути к файлам или папкам.

Относительные пути обсчитываются относительно расположения файла "`project.json`" и записываются по следующим правилам:

1. Разделителем между папками/файлами в пути выступает обратный слэш, однако он должен быть проэкранирован дублированием:

	`"lib\\easy.dialog\\mod.qsp"`

2. Путь не должен начинаться с разделителя (двойной обратный слэш):

	`"lib\\easy.dialog\\mod.qsp"` — так писать можно
	`"\\lib\\easy.dialog\\mod.qsp"` — так писать нельзя

3. Указание на текущую папку (в которой лежит "project.json") производится через точку:

	`"."` - текущая папка

4. Допускается указание текущей папки через точку и относительный путь от этой папки:

	`".\\lib"` — вложенная в текущую папку папка "lib". Равносильно такой записи:
	`"lib"`

5. Используя две точки можно указать папку выше текущей:

	`".."` — папка, в которую вложена текущая

6. Можно указывать папки на несколько уровней вверх, указывая через двойной бэкслэш две точки для каждого уровня:

	`"..\\.."` — на два уровня выше текущей
	`"..\\..\\.."` — на три уровня выше текущей

7. Можно так же указывать папки относительно папок, расположенных выше текущей:

	`"..\\export"` — папка "export", размещённая в одном каталоге с текущей.
	`"..\\..\\project\\other_game\\lib"` — два уровня вверх, и от этой папки в "project\other_game\lib".

##### Пример проекта

В папке "`[disdocs]\example_project`" присутствует пример *разобранного* проекта. Почти все локации разнесены по отдельным файлам и разбросаны в разные папки по функционалу и тематике. Если считать "`[disdocs]\example_project`" за корень, то в корне размещён, помимо остальных папок, файл "`project.json`", который и определяет порядок сборки основного файла игры и файлов модулей.

Попробуйте сделать билд этого проекта, если сомневаетесь, что правильно поняли, как работает билдер. При сборке данного проекта в папке "`[disdocs]\example_game`" будут созданы основной файл игры "`game.sam.qsp`" и файлы различных модулей. Не забудьте прописать свои пути к плееру и утилите TXT2GAM для правильной конвертации и запуска. Если вы используете режим **Build and Run**, файл "`game.sam.qsp`" будет запущен в плеере.

#### Порядок сборки и запуска

Для удобства определены три режима работы QBST:

* **Build and Run** — сборка и запуск
* **Build** — исключительно сборка
* **Run** — исключительно запуск

У каждого из режимов есть свои особенности.

"**Build and Run**" отличается тем, что в этом режиме обязательно собираются заново все файлы "`.qsp`", определённые инструкциями "`project.json`", затем, если в инструкциях неверно указан, или не указан, файл "`.qsp`", который следует запустить (элемент "start"), запускается самый первый определённый инструкциями собранный файл "`.qsp`".

"**Build**" отличается тем, что в этом режиме происходит новая сборка всех файлов "`.qsp`", определённых инструкциями "project.json", и больше ничего.

"**Run**" — в этом режиме не производится новая сборка файлов "`.qsp`", но запускается в плеере тот файл "`.qsp`", который указан в "`project.json`" в элементе "start", либо, если файл указан неверно или не указан совсем, любой выбранный файл "`.qsp`" и открытый во вкладке Sublime Text.

При сборке содержимое файлов формата TXT2GAM добавляется в результирующий файл в следующем порядке:

1. Файлы, перечисленные в массиве элемента "files", по порядку. Таким образом самыми первыми в файле "`.qsp`" оказываются локации из самого первого файла в элементе "files".
	
	Данной особенностью можно воспользоваться, если вам нужно строго определить первую локацию в игре, но порядок остальных вас не волнует. Просто выносите эту локацию в отдельный текстовый файл, а расширение ставите ".txt" или ".start", затем указываете путь к файлу самым первым в массиве элемента "files".

2. Файлы "`.qsps`", "`.qsp-txt`" и ".txt-qsp" содержащиеся в папках, перечисленных в массиве элемента "folders" по порядку, независимо от уровня вложенности. Т.е. если у нас перечисленны по порядку папки "`1`", "`2`" и "`3`", то сначала в результирующий файл добавятся локации из папки "`1`" и всех её вложенных папок, затем из папки "`2`" и всех её вложенных папок, затем из папки "`3`" и всех её вложенных папок.

#### Ошибки

Я решил отказаться от вывода ошибок в консоль, все они выводятся в файл "`errors.log`":

`"main: Start-file is wrong. Don't start the player."` — эта ошибка означает, что стартовый файл не был определён. Она может возникнуть в том случае, если элемент "start" отсутствует в "`project.json`", или путь к файлу указан неверно, при этом QBST запущен в режиме "**Run**", но файл "`.qsp`" не открыт в активной вкладке.
`"main: Path at player is wrong. Prove path '[...]'."` — эта ошибка означает, что путь к плееру указан неверно.
`"main: Start-file is wrong. Used '[...]' for start the player."` — эта ошибка означает, что стартовый файл в элементе "start" не был определён, или он был указан неверно, поэтому после сборки всех файлов "`.qsp`" в плеере будет запущен самый первый из инструкций сборки файл "`.qsp`".
`"main: Key 'build' not found in project-list. Choose export name [...]"` — эта ошибка означает, что не был определён элемент "build" в инструкции сборки, т.е. не предложено имя конечного файла "`.qsp`". В случае этой ошибки имя файла назначается автоматически.

`"function.getFilesList: Folder is empty. Prove path '[...]'."` — функция *getFilesList* не смогла получить список файлов для сборки по указанному пути.
`"function.genFilesPaths: File don't exist. Prove path '[...]'."` — функция *genFilesPaths* не обнаружила файла по указанному пути. Данный файл не существует.
`function.searchProject: not found 'project.json' file for this project. Prove path '[...]'."` — функция *searchProject* не обнаружила файл "`project.json`".

Если всё же в консоли у вас выводятся ошибки, то скорее всего они имеют вот такой вид:

```
Traceback (most recent call last):
  File "D:\my\GameDev\QuestSoftPlayer\projects\JAD\QBST\main.py", line 72, in <module>
    qsp.constructFile(build_files,exit_txt)
  File "D:\my\GameDev\QuestSoftPlayer\projects\JAD\QBST\function.py", line 44, in constructFile
    file.write(text)
  File "C:\Program Files\Python39\lib\encodings\cp1251.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
UnicodeEncodeError: 'charmap' codec can't encode character '\u2191' in position 29347: character maps to <undefined>
```

В данном случае ошибка показывает, что имеются проблемы с декодированием. Сообщите о ней, написав мне на почту aleksversus@mail.ru.

Вообще, на данное время билдер проводит двойную конвертацию utf-8 > cp1251 > (через txt2gam) > utf-16, и при этом теряется часть спецсимволов. Так что будьте аккуратны при работе с билдером, если используете отличную от cp1251 кодировку при разработке проекта.







## Подсветка синтаксиса QSP

Для того, чтобы в ваших файлах формата TXT2GAM с расширениями "`.qsps`", "`.qsp-txt`", или "`.txt-qsp`", автоматически подсвечивался код QSP, необходимо установить пакет подсветки синтаксиса QSP в ваш Sublime Text. Для этого просто скопируйте файл "`QSP.sublime-package`" из папки "`Syntax-Light`" в папку "`Packages`" в месте установки вашего Sublime Text. Например, у меня эта папка лежит по адресу "`C:\Program Files\Sublime Text\Packages`".

Вы можете видеть, что в папке "`Syntax-Light`" лежит файл "`QSP.tmLanguage`" — это непосредственно сам файл подсветки, но если вы скопируете его в папку "`Packages`", подсветка работать не будет.

Сам файл "`QSP.sublime-package`" представляет собой zip-архив с изменённым расширением. Именно из него подхватывается подсветка QSP-кода.
Файл "`QSP.tmLanguage`" представляет собой XML-файл с изменённым расширением. Т.е. вы вполне можете отредактировать его самостоятельно через тот же Sublime-Text и упаковать в "`.sublime-package`", создав таким образом собственную подсветку синтаксиса.

Подсветку синтаксиса я ещё буду перерабатывать, поскольку сейчас в ней не учтены многие особенности кода QSP, а так же различных цветовых схем Sublime Text. Более-менее сносно подсветка будет работать в цветовой схеме "Monokai".

## Совместная разработка и контроль версий

Для более подробных сведений о совместной разработке, вам необходимо ознакомиться с системами Git, github, и иными, более подробно. Здесь приводятся лишь основные моменты, с которых могут начать новички.

### Контроль версий

Для контроля версий разрабатываемой игры необходимо установить на своём компьютере Git. Нижеследующие пункты взяты из инструкции https://htmlacademy.ru/blog/boost/frontend/git-console и ориентированы на пользователей Windows:

1. Скачиваем установщик со страницы https://git-scm.com/download/win
2. Устанавливаем программу, и при установке можем отметить или снять пункты "Windows Explorer integration":
	* "Git Bash Here" — пункт контекстного меню, который запустит косноль git bash в указанной папке
	* "Git GUI Here" — пункт контекстного меню, который запустит git с графическим интерфейсом в указанной папке
3. Ещё при установке можно выбрать редактор по умолчанию. Я выбирал Sublime Text, и если вы уже установили Sublime Text и теперь впервые устанавливаете Git, то так же выбирайте его. Остальные пункты можно оставить без изменения.
4. После установки Git можете добавить user.name и user.email для всех своих проектов через командную строку Windows или Git CMD, хотя в принципе это не обязательно. См. https://htmlacademy.ru/blog/boost/frontend/git-console

5. Для пробы можете создать новый репозиторий. Для этого:
	* создайте любую пустую папку. Например, я храню все проекты на диске `D:` в папке "`projects`", поэтому для нового репозитория я создал папку "`new_rep`" ("`D:\projects\new_rep`").
	* откройте командную строку Windows или Git CMD и перейдите в указанный каталог с помощью команды "`cd`":
		`cd "D:\projects\new_rep"`

	* инициализируйте создание нового репозитория (данная команда создаст репозиторий, даже если в папке уже есть содержимое):
		`git init`

Собственно это всё, что нужно для контроля версий. В интернете есть много информации о работе с Git, и в принципе, если вам удобно вести контроль версий, используя консоль, то вам будет достаточно Git Bash. Кое-кому удобен даже Git GUI. Однако...

#### Sublime Merge

...если вы откроете один из файлов вашего проекта (репозитория) в Sublime Text, то в строке состояния вы увидите особую отметку, которая показывает число изменённых файлов проекта. Если вы добавите новый файл в тестовый репозиторий "`new_rep`", то эта отметка будет выглядеть, как "`|1|master`" — то есть 1 изменение в master-ветке проекта.

Дело в том, что Sublime Text автоматически подхватывает списки изменений из Git (условно говоря). Если вы щёлкнете по отметке об изменениях, Sublime Text предложит вам скачать Sublime Merge. Обязательно скачайте и установите, так как Sublime Merge в совокупности с Sublime Text является более удобным Git-клиентом.

По сути Git-клиент — это приложение, которое взаимодействует с системой Git, чтобы обеспечивать вам наглядное и удобное управление вашими репозиториями. Это что-то вроде внешнего GUI для Git.

Любое или все изменения можно закоммитить (зафиксировать в истории изменений), используя Sublime Merge. Для этого отмечаете нужные файлы и изменения в них, вводите текст коммита и нажимаете кнопку "Commit". Если вы ещё не указывали "user.name" и "user.email", Sublime Merge предложит вам сделать это.

### Совместная разработка

Теперь, когда у вас есть все инструменты для контроля версий, осталось организовать совместную разработку. Я предлагаю воспользоваться системой github, как наиболее удобным для новичков хранилищем репозиториев.

Всем разработчикам придётся зарегистрировать по одному аккаунту на github. Один из разработчиков должен создать репозиторий для совместной разработки игры. При этом можно выбрать опцию "Private" (репозиторий будет доступен для просмотра вам и выбранным людям) или "Public" (репозиторий смогут просматривать все).

Разработчик, создавший репозиторий, должен выслать приглашения остальным разработчикам. Это делается в разделе GitHub "Settings" — "Manage Access"

Когда у всех разработчиков появляется доступ к репозиторию, каждому нужно зайти в Sublime Merge открыть меню "File" - "Clone Repository", откроется вкладка, в которой нужно указать URL репозитория и другие параметры доступа, например SSH-ключ.

### Заключение

Данное руководство будет пополняться подробностями по мере возникновения вопросов. На самом деле тема Совместной разработки слишком обширна, чтобы осветить её здесь хоть сколько-нибудь подробно. Я и сам не вполне разобрался со многими вопросами. Но, если у вас есть, что спросить, пишите на aleksversus@mail.ru, помогу чем смогу, а ваши вопросы помогут улучшить текст данного руководства.

Пишите обязательно, если у вас есть советы или замечания по работе QBST, по наполнению данного руководства и иные.


## P.S.:

[здесь будет вставлена ссылка на видео]

* Канал на YouTube обучающий писать игры на QSP: https://www.youtube.com/c/aleksversus

* Сайт с текстовыми играми и программами для создания игр: http://qsp.su
* Наша группа в vk: https://vk.com/qsplayer
* В дискорде https://discord.gg/SMvzEFm

* Обсуждение справочника "Как сделать? Ча.Во." на форуме http://qsp.su/index.php?option=com_agora&task=topic&id=1280&p=1&prc=25&Itemid=57
* Скачать справочник на mega.nz: https://mega.nz/folder/vG4XzSoZ#gf0jU0FFdWHpgJnN8eAaGA
* Примеры кода и различные решения: https://mega.nz/folder/rfAllKzR#rssaaJSs4tpGA_tUbaCCQw
* Программы: https://mega.nz/folder/jXwXlSRJ#TF7P-soOJOWIC8MrBA-L1A

* Обучение HTML и CSS, плюс немного JS https://mega.nz/folder/WXhkWLSI#WmF8uN01JeuIyopuCtGlMw

Новые версии плеера:

* Nex (Quest Navigator): http://qsp.su/index.php?option=com_agora&task=topic&id=633&Itemid=57
* WereWolf (QSPider): http://qsp.su/index.php?option=com_agora&task=topic&id=1291&Itemid=57
* Sonnix (Плеер с поддержкой webm): http://qsp.su/index.php?option=com_agora&task=topic&id=1192&p=1&prc=25&Itemid=57#p26813
* Seedheartha (Quest Player Fork): http://qsp.su/index.php?option=com_agora&task=topic&id=128&p=10&prc=25&Itemid=57#p27855

Поблагодарите отца-основателя платформы Байта: http://qsp.su/index.php?option=com_comprofiler&Itemid=20&user=66

А так же простимулируйте разработку нового QGen от Rrock: http://qsp.su/index.php?option=com_agora&task=topic&id=594&Itemid=57

Анонс шикарнейшей игры от Svartbergа на классическом плеере: http://qsp.su/index.php?option=com_agora&task=topic&id=1235&Itemid=57

* Единоразово задарить меня https://www.donationalerts.com/r/aleksversus
* Задаривать ежемесячно https://boosty.to/aleksversus