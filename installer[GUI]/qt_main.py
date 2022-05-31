import sys

from PyQt5 import QtWidgets # импортировали класс, с помощью которого можно создавать объекты GUI
from PyQt5.QtWidgets import QApplication # данный класс позволит создать само приложение
from PyQt5.QtWidgets import QMainWindow # данный класс позволит создать окно графической оболочки

def btn_click():
	# функция обеспечивающая функциональность кнопки
	print("Нажал!")


def application():
	# основная функция, которая будет вызываться при запуске приложения
	app = QApplication(sys.argv) # создаём объект приложение и в качестве аргумента ему передаём список аргументов из sys
	window = QMainWindow() # создаём объект окно
	# задаём заголовок окна
	window.setWindowTitle("Установка QBST и Sublime-Package")
	# задаём расположение окна
	window.setGeometry(250, 250, 500, 200)
	
	# выводим надпись в окно
	main_text = QtWidgets.QLabel(window) # создаём объект
	main_text.setText("Установка QBST и Sublime-Package") # устанавливаем текст надписи
	main_text.move(100,100) # вравниваем в окне относительно верха и левого края
	main_text.adjustSize() # подстраиваем ширину объекта под содержимое

	# добавляем кнопку
	btn = QtWidgets.QPushButton(window) # создаём объект
	btn.setText("Укажите путь к Sublime Text")
	btn.move(250,150)
	btn.setFixedWidth(200) # устанавливаем фиксированную ширину кнопки 200 пикселей
	btn.clicked.connect(btn_click) # делаем связку функции и события

	# чтобы показать окно, необходимо применить следующий метод
	window.show()
	# необходимо предусмотреть корректный выход из программы
	sys.exit(app.exec_())


if __name__ == "__main__":
	application()