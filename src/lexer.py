"""
Лексический анализатор для ArduinoScript
"""
import re
from keywords import KEYWORDS

class Token:
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f"Token({self.type}, '{self.value}', line={self.line}, col={self.column})"

class Lexer:
    def __init__(self, code):
        self.code = code
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        
        # Регулярные выражения для токенов
        self.token_specs = [
            # Пропускаемые символы
            ('WHITESPACE', r'[ \t]+'),
            ('NEWLINE',    r'\n'),
            
            # Комментарии
            ('COMMENT',    r'//[^\n]*'),
            ('ML_COMMENT', r'/\*[\s\S]*?\*/'),
            
            # Числа
            ('FLOAT',      r'\d+\.\d+'),
            ('INTEGER',    r'\d+'),
            ('HEX',        r'0x[0-9A-Fa-f]+'),
            ('BINARY',     r'0b[01]+'),
            
            # Строки
            ('STRING',     r'"[^"]*"'),
            ('CHAR',       r"'[^']'"),
            
            # Операторы
            ('ASSIGN',     r'='),
            ('PLUS',       r'\+'),
            ('MINUS',      r'-'),
            ('MULTIPLY',   r'\*'),
            ('DIVIDE',     r'/'),
            ('MODULO',     r'%'),
            ('POWER',      r'\*\*'),
            
            # Операторы сравнения
            ('EQ',         r'=='),
            ('NEQ',        r'!='),
            ('LT',         r'<'),
            ('LTE',        r'<='),
            ('GT',         r'>'),
            ('GTE',        r'>='),
            
            # Логические операторы
            ('AND',        r'&&'),
            ('OR',         r'\|\|'),
            ('NOT',        r'!'),
            
            # Скобки и разделители
            ('LPAREN',     r'\('),
            ('RPAREN',     r'\)'),
            ('LBRACE',     r'{'),
            ('RBRACE',     r'}'),
            ('LBRACKET',   r'\['),
            ('RBRACKET',   r'\]'),
            ('COMMA',      r','),
            ('COLON',      r':'),
            ('SEMICOLON',  r';'),
            ('DOT',        r'\.'),
            ('ARROW',      r'->'),
            
            # Специальные символы
            ('PIN_PREFIX', r'[DA]\d+'),  # D13, A0 и т.д.
            
            # Идентификаторы и ключевые слова
            ('ID',         r'[a-zA-Zа-яА-Я_][a-zA-Zа-яА-Я0-9_]*'),
        ]
        
        # Собираем все регулярные выражения в одно
        self.token_regex = re.compile(
            '|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.token_specs)
        )
    
    def tokenize(self):
        """Разбивает исходный код на токены"""
        for match in self.token_regex.finditer(self.code):
            kind = match.lastgroup
            value = match.group()
            
            # Позиция в исходном коде
            line = self.line
            column = self.column
            
            # Обновляем позицию для следующего токена
            if kind == 'NEWLINE':
                self.line += 1
                self.column = 1
                continue
            elif kind == 'WHITESPACE':
                self.column += len(value)
                continue
            elif kind in ('COMMENT', 'ML_COMMENT'):
                # Подсчитываем количество строк в комментарии
                lines = value.count('\n')
                self.line += lines
                self.column = 1 if lines > 0 else self.column + len(value)
                continue
            else:
                self.column += len(value)
            
            # Обработка токенов
            if kind == 'ID':
                # Проверяем, является ли идентификатор ключевым словом
                if value in KEYWORDS:
                    kind = KEYWORDS[value]
            
            elif kind == 'INTEGER':
                value = int(value)
            elif kind == 'FLOAT':
                value = float(value)
            elif kind == 'HEX':
                value = int(value, 16)
            elif kind == 'BINARY':
                value = int(value, 2)
            elif kind == 'STRING':
                value = value[1:-1]  # Убираем кавычки
            elif kind == 'CHAR':
                value = value[1:-1]
            
            # Создаем токен
            token = Token(kind, value, line, column)
            self.tokens.append(token)
        
        # Добавляем конечный токен
        self.tokens.append(Token('EOF', '', self.line, self.column))
        return self.tokens
    
    def peek(self, n=1):
        """Просмотр следующих n токенов"""
        if self.pos + n - 1 < len(self.tokens):
            return self.tokens[self.pos + n - 1]
        return None
    
    def advance(self):
        """Переход к следующему токену"""
        if self.pos < len(self.tokens):
            token = self.tokens[self.pos]
            self.pos += 1
            return token
        return None
    
    def expect(self, expected_type, error_msg=None):
        """Проверяет, что текущий токен имеет ожидаемый тип"""
        token = self.peek()
        if token and token.type == expected_type:
            return self.advance()
        
        if not error_msg:
            error_msg = f"Ожидался {expected_type}, получен {token.type if token else 'EOF'}"
        raise SyntaxError(f"Строка {token.line}:{token.column} - {error_msg}")

if __name__ == "__main__":
    # Тестирование лексера
    test_code = """
    // Тестовая программа
    пин D13 = выход
    цифрзапись(D13, высоко)
    ждать(1000)
    """
    
    lexer = Lexer(test_code)
    tokens = lexer.tokenize()
    
    for token in tokens:
        print(token)
