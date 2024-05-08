#ifndef __QGC_PLUGIN_API_PREPROCESSOR_H__
#define __QGC_PLUGIN_API_PREPROCESSOR_H__

#pragma once
#include "QGC_Plugin_API.h"

/* ------------------------------- ПЛАГИНЫ ПРЕДВАРИТЕЛЬНОЙ ОБРАБОТКИ ------------------------------- */
/*
* Назначение режима:
*	*. Работа с текстом
*/

struct QGCP_QSP_LOCATIONS {                                          // # Структура описания массива указателей на локации
	struct TLOCATION {                                               // # Структура описания локации
		QGCP_CHARARRAY* pName = nullptr;                             // Указатель на структуру QGCP_CHARARRAY с названием
		QGCP_CHARARRAY* pCode = nullptr;                             // Указатель на структуру QGCP_CHARARRAY с содержимым
	};

	TLOCATION** lpLocations = nullptr;                               // Указатель на указатель на структуру TLOCATION
	uint32_t nLocations = 0;                                         // Количество элементов в lpLocations
};

/*
* Эта функция вызывается, когда происходит обработка игровой локации или содержимого текстового файла.
* 
* Функция должна возвращать значение:
*     true (истина) - Если локацию не требуется удалить, а переменная pOutLocations содержит данные локации.
*     false (ложь)  - Если локацию требуется удалить, а переменная pOutLocations не содержит никаких данных.
* Если плагин не обработал данные в pInLocations, то он все равно должен вернуть true и заполнить переменную pOutLocations в том случае, если эта локация необходима для сохранения.
* 
* Параметры:
*      pInLocations
*           Данный параметр содержит обрабатываемую локацию (в режиме QGCP_INFO::TWORKER::pwDisassemble) или содержимое текстового файла (в режиме QGCP_INFO::TWORKER::pwAssemble).
*           Всегда содержит данные одной локации.
*           Освобождение памяти данной переменной осуществляет программа.
*           Плагин не должен как-либо изменять данные в этой переменной.
*      pOutLocations
*           Плагин должен выделить память и заполнить переменную, содержимое которой будет использоваться в дальнейшем.
*           Освобождение памяти данной переменной осуществляет плагин, в последующем вызове программой функции pluginFreeQspLocations.
*/
DLL_EXPORT bool pluginParseQspLocations(QGCP_QSP_LOCATIONS*& pInLocations, QGCP_QSP_LOCATIONS*& pOutLocations);

/*
* Эта функция вызывается для полного очищения и освобождения данных из памяти.
* Эта функция вызывается, если плагин вернул значение true (истина) как результат работы функции pluginParseQspLocations, и содержит переменную pOutLocations.
*/
DLL_EXPORT void pluginFreeQspLocations(QGCP_QSP_LOCATIONS*& pLocations);

#endif