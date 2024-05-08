#include "QSP_GameFile.h"

/*--------------------------------------------------------------------------------------------------*/

// ---- | Преобразование массива QSP_CHAR в расширенную строку
std::wstring __qspcharToWstring(QSP_CHAR* szData, uint32_t nSize) {
	std::wstring wsResult;

	for (uint32_t i = 0; i < nSize; i++) {
		wsResult += szData[i];
	}

	return wsResult;
}

// ---- | Получение и удаление подстроки из строки (с удалением разделителя)
std::wstring _substring(std::wstring& wsSource) {
	std::wstring wsResult;

	uint32_t nPos = wsSource.find(L"\r\n");
	if (nPos != std::wstring::npos) {
		wsResult = wsSource.substr(0, nPos);
		wsSource.erase(0, nPos + 2);
	}

	return wsResult;
}

// ---- | Расшифровка и разделение расширенной строки на вектор расширенных строк
std::vector<std::wstring> _splitWithDecode(std::wstring& wsData) {
	std::vector<std::wstring> vwsResult;

	uint32_t nPos = 0;
	while ((nPos = wsData.find(L"\r\n")) != std::wstring::npos) {
		vwsResult.push_back(QSP::GameFile::decodeString(wsData.substr(0, nPos)));
		wsData.erase(0, nPos + 2);
	}

	return vwsResult;
}

template<class _T>
void freePointer(_T*& pValue) {
	if (pValue != nullptr) {
		delete pValue;
		pValue = nullptr;
	}
}

template<class _T>
void freePointerArray(_T*& parValue) {
	if (parValue != nullptr) {
		delete[] parValue;
		parValue = nullptr;
	}
}

void freeString(std::wstring& wsSource) {
	wsSource.clear();
	std::wstring(wsSource).swap(wsSource);
}

template<typename _T>
void freeVector(std::vector<_T>& Vector) {
	typename std::vector<_T>(Vector).swap(Vector);
}

/*--------------------------------------------------------------------------------------------------*/

// ---- |
TQSPGAME::TACTION::~TACTION() {
	freeString(this->wsImage);
	freeString(this->wsName);
	freeString(this->wsCode);
}

// ---- |
TQSPGAME::TLOCATION::~TLOCATION() {
	freeString(this->wsName);
	freeString(this->wsDescription);
	freeString(this->wsCode);
	this->nActions = 0;

	for (size_t k = this->vpActions.size(); k > 0; k--) {
		freePointer(this->vpActions.at(k - 1));
		this->vpActions.erase(vpActions.begin() + (k - 1));
	}
	freeVector(this->vpActions);
}

// ---- |
TQSPGAME::~TQSPGAME() {
	freeString(this->wsHeader);
	freeString(this->wsVersion);
	freeString(this->wsPassword);
	this->nLocations = 0;

	for (size_t i = this->vpLocations.size(); i > 0; i--) {
		freePointer(this->vpLocations.at(i - 1));
		this->vpLocations.erase(this->vpLocations.begin() + (i - 1));
	}
	freeVector(this->vpLocations);
}

/*--------------------------------------------------------------------------------------------------*/

namespace QSP {

	namespace GameFile {

		// ---- |
		int decodeInteger(std::wstring& wsData) {
			return _wtoi(QSP::GameFile::decodeString(wsData).c_str());
		}

		// ---- |
		std::wstring decodeString(std::wstring& wsData) {
			std::wstring wsResult;

			for (size_t i = 0; i < wsData.size(); i++) {
				if (wsData.at(i) == -QSP_CAESARCIPHER) {
					wsResult += QSP_CAESARCIPHER;
				} else {
					wsResult += wsData.at(i) + QSP_CAESARCIPHER;
				}
			}

			return wsResult;
		}

		// ---- |
		std::wstring decodeChars(QSP_CHAR* arData, uint32_t nSize) {
			std::wstring wsResult;

			for (uint32_t i = 0; i < nSize; i++) {
				if (arData[i] == -QSP_CAESARCIPHER) {
					wsResult += QSP_CAESARCIPHER;
				} else {
					wsResult += arData[i] + QSP_CAESARCIPHER;
				}
			}

			return wsResult;
		}

		// ---- |
		bool fileRead(const wchar_t* pwszFile, TQSPGAME* pQspGame) {
			freePointer(pQspGame);

			std::ifstream* pifs = new std::ifstream();
			pifs->open(pwszFile, std::fstream::binary);
			if (!pifs->is_open()) {
				freePointer(pifs);
				return false;
			}

			pQspGame = new TQSPGAME();

			// Получение и запись первых 14 байт с последующим сравнением их с эталоном
			QSP_CHAR szHeader[8] = { 0 };
			pifs->read(reinterpret_cast<char*>(&szHeader), 14);
			pQspGame->wsHeader = __qspcharToWstring(szHeader, 7);
			if (pQspGame->wsHeader.compare(L"QSPGAME") != 0) {
				freePointer(pQspGame);
				freePointer(pifs);
				return false;
			}

			// Сдвиг позиции чтения в файле на 4 байта
			std::streampos nFilePos = pifs->tellg();
			nFilePos += 4;

			// Получение размера всего файла
			pifs->seekg(0, pifs->end);
			std::streampos nFileSize = pifs->tellg();
			pifs->seekg(nFilePos);

			// Чтение всех оставшихся байт из файла
			uint32_t nSize = nFileSize / 2 - 7;
			QSP_CHAR* pqchData = new QSP_CHAR[nSize + 1];
			memset(&pqchData[0], 0, nSize + 1);
			pifs->read(reinterpret_cast<char*>(&*pqchData), nSize * 2);

			//
			std::wstring wsData = __qspcharToWstring(pqchData, nSize);
			freePointerArray(pqchData);

			// Получение версии утилиты, сохранившей файл
			pQspGame->wsVersion = _substring(wsData);

			//
			std::vector<std::wstring> vwsData = _splitWithDecode(wsData);
			freeString(wsData);

			// Получение пароля к файлу игры
			pQspGame->wsPassword = vwsData.at(0);

			// Получение количества локаций
			pQspGame->nLocations = _wtoi(vwsData.at(1).c_str());

			// Получение локаций (вместе с именем, описанием, кодом и действиями)
			for (uint32_t i = 2; i < vwsData.size();) {
				try {
					TQSPGAME::TLOCATION* pLocation = new TQSPGAME::TLOCATION();
					pLocation->wsName = vwsData.at(i++);
					pLocation->wsDescription = vwsData.at(i++);
					pLocation->wsCode = vwsData.at(i++);
					pLocation->nActions = _wtoi(vwsData.at(i++).c_str());

					try {
						for (uint32_t k = 0; k < pLocation->nActions; k++) {
							TQSPGAME::TACTION* pAction = new TQSPGAME::TACTION();
							pAction->wsImage = vwsData.at(i++);
							pAction->wsName = vwsData.at(i++);
							pAction->wsCode = vwsData.at(i++);

							pLocation->vpActions.push_back(pAction);
						}
					} catch (...) {
						pLocation->nActions = 0;
					}

					pQspGame->vpLocations.push_back(pLocation);
				} catch (...) {
					freePointer(pifs);
					freePointer(pQspGame);
					return false;
				}
			}

			freePointer(pifs);
			return true;
		}

	}

}