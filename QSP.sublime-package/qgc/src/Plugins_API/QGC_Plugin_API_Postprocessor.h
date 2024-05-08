#ifndef __QGC_PLUGIN_API_POSTPROCESSOR_H__
#define __QGC_PLUGIN_API_POSTPROCESSOR_H__

#pragma once
#include "QGC_Plugin_API.h"

/* --------------------------------- ПЛАГИНЫ ПОСЛЕДУЮЩЕЙ ОБРАБОТКИ --------------------------------- */
/*
* Назначение режима:
*	*. Работа с файлами
*/

struct QGCP_FILES {                                                  // # Структура описания массива указателей на файлы
	enum TTYPE {                                                     // # Перечисление типов файлов
		ftInput,                                                     // Файлы являются вводными
		ftOutput,                                                    // Файлы являются конечными
	};

	TTYPE eType = ftInput;                                           // Тип файлов
	QGCP_CHARARRAY** lpFiles = nullptr;                              // Указатель на указатель на структуру QGCP_CHARARRAY
	uint32_t nFiles = 0;                                             // Количество элементов в lpFiles
};

/*
* Параметры:
*      pFiles
*           Данный параметр содержит файл(ы), обрабатываемые в программе.
*           Освобождение памяти данной переменной осуществляет программа.
*           Плагин не должен как-либо изменять данные в этой переменной.
*/
DLL_EXPORT void pluginProcessFiles(QGCP_FILES*& pFiles);

#endif