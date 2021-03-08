import os

building=['D:\\my\\GameDev\\QuestSoftPlayer\\projects\\JAD\\build-example\\fb_v0.2.1.qsps',
'D:\\my\\GameDev\\QuestSoftPlayer\\projects\\JAD\\build-example\\локации места\\дом.txt-qsp',
'D:\\my\\GameDev\\QuestSoftPlayer\\projects\\JAD\\build-example\\обязательные локации\\help.qsps',
'D:\\my\\GameDev\\QuestSoftPlayer\\projects\\JAD\\build-example\\обязательные локации\\[chest]\\chest.qsps',
'D:\\my\\GameDev\\QuestSoftPlayer\\projects\\JAD\\build-example\\обязательные локации\\[death]\\death.qsps',
'D:\\my\\GameDev\\QuestSoftPlayer\\projects\\JAD\\build-example\\системное меню\\sys_menu.qsp-txt',
'D:\\my\\GameDev\\QuestSoftPlayer\\projects\\JAD\\drive\\drive.qsps']

def constructFile(build_list):
	# получив список файлов из которых мы собираем выходной файл, делаем следующее
	# каждый файл открываем
	for file in build_list:
		with open(file,"r") as text:
			print (text.read())

constructFile(building)