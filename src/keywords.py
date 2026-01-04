"""
Ключевые слова и команды ArduinoScript
"""

KEYWORDS = {
    # Основные конструкции
    'цикл': 'LOOP',
    'функция': 'FUNCTION',
    'если': 'IF',
    'иначе': 'ELSE',
    'иначе_если': 'ELIF',
    'для': 'FOR',
    'пока': 'WHILE',
    'прервать': 'BREAK',
    'продолжить': 'CONTINUE',
    'вернуть': 'RETURN',
    'конец': 'END',
    
    # Типы данных
    'целое': 'INT',
    'дробное': 'FLOAT',
    'булево': 'BOOL',
    'символ': 'CHAR',
    'строка': 'STRING',
    'массив': 'ARRAY',
    'пусто': 'VOID',
    
    # Константы
    'истина': 'TRUE',
    'ложь': 'FALSE',
    'высоко': 'HIGH',
    'низко': 'LOW',
    'включено': 'ON',
    'выключено': 'OFF',
    
    # Пин-режимы
    'вход': 'INPUT',
    'выход': 'OUTPUT',
    'вход_подтяжка': 'INPUT_PULLUP',
    'аналог': 'ANALOG',
    'шим': 'PWM',
    
    # Команды Arduino
    'пин': 'PIN',
    'режим': 'PINMODE',
    'цифрзапись': 'DIGITALWRITE',
    'цифрчтение': 'DIGITALREAD',
    'аналогзапись': 'ANALOGWRITE',
    'аналогчтение': 'ANALOGREAD',
    'ждать': 'DELAY',
    'миллис': 'MILLIS',
    'микрос': 'MICROS',
    'прерывание': 'ATTACHINTERRUPT',
    'отключить_прерывание': 'DETACHINTERRUPT',
    'пауза': 'PAUSE',
    'случайное': 'RANDOM',
    
    # Serial команды
    'последовательный': 'SERIAL',
    'начать_последовательный': 'SERIAL_BEGIN',
    'печать': 'PRINT',
    'печать_строка': 'PRINTLN',
    'доступно': 'AVAILABLE',
    'читать': 'READ',
    'найти': 'FIND',
    'найти_до': 'FIND_UNTIL',
    'очистить': 'FLUSH',
    
    # Математические функции
    'пи': 'PI',
    'макс': 'MAX',
    'мин': 'MIN',
    'ограничить': 'CONSTRAIN',
    'отобразить': 'MAP',
    'степень': 'POW',
    'квадрат': 'SQ',
    'корень': 'SQRT',
    'абсолют': 'ABS',
    'синус': 'SIN',
    'косинус': 'COS',
    'тангенс': 'TAN',
    'случайное_семя': 'RANDOM_SEED',
    
    # Битовые операции
    'бит_читать': 'BITREAD',
    'бит_записать': 'BITWRITE',
    'бит_установить': 'BITSET',
    'бит_очистить': 'BITCLEAR',
    
    # Прерывания
    'изменить': 'CHANGE',
    'возрастание': 'RISING',
    'убывание': 'FALLING',
    
    # Время
    'секунды': 'SECONDS',
    'минуты': 'MINUTES',
    'часы': 'HOURS',
    
    # Логические операторы
    'и': 'AND',
    'или': 'OR',
    'не': 'NOT',
    'больше': 'GT',
    'меньше': 'LT',
    'равно': 'EQ',
    'не_равно': 'NEQ',
    'больше_равно': 'GTE',
    'меньше_равно': 'LTE',
}

# Номера пинов по умолчанию
PIN_ALIASES = {
    'светодиод': 13,
    'кнопка': 2,
    'потенциометр': 'A0',
    'термистор': 'A1',
    'фоторезистор': 'A2',
    'зуммер': 3,
    'серво': 9,
    'ультразвук_триггер': 10,
    'ультразвук_эхо': 11,
    'дисплей_sda': 'A4',
    'дисплей_scl': 'A5',
}

# Встроенные функции Arduino
ARDUINO_FUNCTIONS = [
    'pinMode', 'digitalWrite', 'digitalRead',
    'analogWrite', 'analogRead', 'delay',
    'delayMicroseconds', 'millis', 'micros',
    'attachInterrupt', 'detachInterrupt',
    'random', 'randomSeed', 'map', 'constrain',
    'abs', 'sin', 'cos', 'tan', 'sqrt', 'pow',
    'min', 'max', 'Serial.begin', 'Serial.print',
    'Serial.println', 'Serial.available', 'Serial.read',
    'tone', 'noTone', 'pulseIn', 'shiftOut',
    'shiftIn', 'analogReference',
]