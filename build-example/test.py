# файл для тестирования python-скриптов

import timeit

code="import main"

et=timeit.timeit(code, number=100)/100
print (et)




