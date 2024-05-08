#ifndef __QSP_GAMEFILE_H__
#define __QSP_GAMEFILE_H__

#pragma once
#include <vector>
#include <string>
#include <fstream>

typedef uint16_t QSP_CHAR;                                           // Тип данных QSP для представления символа
const QSP_CHAR QSP_CAESARCIPHER = 5;                                 // Сдвиг для Шифра Цезаря (он же - "ROT")

struct TQSPGAME {                                                    // # QSP файл игры
	std::wstring wsHeader;                                           // Заголовок файла
	std::wstring wsVersion;                                          // Утилита, сохранившая файл
	std::wstring wsPassword;                                         // Пароль к файлу игры
	uint32_t nLocations = 0;                                         // Количество локаций в игре

	struct TACTION {                                                 // # Действие
		std::wstring wsImage;                                        // Изображение
		std::wstring wsName;                                         // Название
		std::wstring wsCode;                                         // Код

		// ---- | Деструктор структуры TACTION
		~TACTION();
	};

	struct TLOCATION {                                               // # Локация
		std::wstring wsName;                                         // Название
		std::wstring wsDescription;                                  // Описание
		std::wstring wsCode;                                         // Код
		uint32_t nActions = 0;                                       // Количество действий в локации (статических)
		
		std::vector<TACTION*> vpActions;                             // Вектор указателей на структуры действий

		// ---- | Деструктор структуры TLOCATION
		~TLOCATION();
	};

	std::vector<TLOCATION*> vpLocations;                             // Вектор указателей на структуры локаций

	// ---- | Деструктор структуры TQSPGAME
	~TQSPGAME();
};

namespace QSP {

	namespace GameFile {

		// ---- | Расшифровка расширенной строки с преобразованием в int
		int decodeInteger(std::wstring& wsData);
		// ---- | Расшиврока расширенной строки
		std::wstring decodeString(std::wstring& wsData);
		// ---- | Расшифровка массива QSP_CHAR
		std::wstring decodeChars(QSP_CHAR* arData, uint32_t nSize);
		// ---- | Чтение QSP файла игры
		bool fileRead(const wchar_t* pwszFile, TQSPGAME* pQspGame);

	}

}

#endif