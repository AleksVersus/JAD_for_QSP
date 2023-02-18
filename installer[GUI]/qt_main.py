import sys

from PyQt5 import QtWidgets # импортировали класс, с помощью которого можно создавать объекты GUI
from PyQt5.QtWidgets import QApplication # данный класс позволит создать само приложение
from PyQt5.QtWidgets import QMainWindow # данный класс позволит создать окно графической оболочки

class Window_app(QMainWindow):
	# создаём класс, наследуя от QMainWindow
	def __init__(self):
		# создаём метод-конструктор, который должен полностью дублировать конструктор родительского класса
		super(Window_app, self).__init__()
		# задаём заголовок окна
		self.setWindowTitle("Установка QBST и Sublime-Package")
		# задаём расположение окна
		self.setGeometry(250, 250, 500, 200)
		
		self.text_msg = QtWidgets.QLabel(self)

		# выводим надпись в окно
		self.main_text = QtWidgets.QLabel(self) # создаём объект
		self.main_text.setText("Установка QBST и Sublime-Package") # устанавливаем текст надписи
		self.main_text.move(100,100) # вравниваем в окне относительно верха и левого края
		self.main_text.adjustSize() # подстраиваем ширину объекта под содержимое

		# добавляем кнопку
		self.btn = QtWidgets.QPushButton(self) # создаём объект
		self.btn.setText("Укажите путь к Sublime Text")
		self.btn.move(250,150)
		self.btn.setFixedWidth(200) # устанавливаем фиксированную ширину кнопки 200 пикселей
		self.btn.clicked.connect(self.btn_click) # делаем связку функции и события

	def btn_click(self):
		# функция обеспечивающая функциональность кнопки
		self.text_msg.setText("вторая надпись")
		self.text_msg.move(50,50) # вравниваем в окне относительно верха и левого края
		self.text_msg.adjustSize() # подстраиваем ширину объекта под содержимое

def application():
	# основная функция, которая будет вызываться при запуске приложения
	app = QApplication(sys.argv) # создаём объект приложение и в качестве аргумента ему передаём список аргументов из sys
	window = Window_app() # создаём объект окно
	# чтобы показать окно, необходимо применить следующий метод
	window.show()
	# необходимо предусмотреть корректный выход из программы
	sys.exit(app.exec_())


if __name__ == "__main__":
	application()
