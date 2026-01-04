"""
Синтаксический анализатор для ArduinoScript
"""
from lexer import Lexer, Token

class ASTNode:
    """Базовый класс для узлов AST"""
    def __init__(self, token=None):
        self.token = token
        self.children = []
    
    def add_child(self, node):
        self.children.append(node)
    
    def __repr__(self):
        return f"{self.__class__.__name__}"

class ProgramNode(ASTNode):
    """Корневой узел программы"""
    pass

class PinDeclarationNode(ASTNode):
    """Объявление пина"""
    def __init__(self, pin, mode, value=None):
        super().__init__()
        self.pin = pin
        self.mode = mode
        self.value = value
    
    def __repr__(self):
        return f"PinDeclaration(pin={self.pin}, mode={self.mode}, value={self.value})"

class DigitalWriteNode(ASTNode):
    """Цифровая запись"""
    def __init__(self, pin, value):
        super().__init__()
        self.pin = pin
        self.value = value
    
    def __repr__(self):
        return f"DigitalWrite(pin={self.pin}, value={self.value})"

class DigitalReadNode(ASTNode):
    """Цифровое чтение"""
    def __init__(self, pin):
        super().__init__()
        self.pin = pin
    
    def __repr__(self):
        return f"DigitalRead(pin={self.pin})"

class AnalogWriteNode(ASTNode):
    """Аналоговая запись (PWM)"""
    def __init__(self, pin, value):
        super().__init__()
        self.pin = pin
        self.value = value
    
    def __repr__(self):
        return f"AnalogWrite(pin={self.pin}, value={self.value})"

class AnalogReadNode(ASTNode):
    """Аналоговое чтение"""
    def __init__(self, pin):
        super().__init__()
        self.pin = pin
    
    def __repr__(self):
        return f"AnalogRead(pin={self.pin})"

class DelayNode(ASTNode):
    """Задержка"""
    def __init__(self, duration):
        super().__init__()
        self.duration = duration
    
    def __repr__(self):
        return f"Delay({self.duration})"

class SerialBeginNode(ASTNode):
    """Инициализация Serial"""
    def __init__(self, baud_rate):
        super().__init__()
        self.baud_rate = baud_rate
    
    def __repr__(self):
        return f"SerialBegin({self.baud_rate})"

class SerialPrintNode(ASTNode):
    """Вывод в Serial"""
    def __init__(self, value, newline=False):
        super().__init__()
        self.value = value
        self.newline = newline
    
    def __repr__(self):
        return f"SerialPrint({self.value}, newline={self.newline})"

class LoopNode(ASTNode):
    """Основной цикл"""
    pass

class IfNode(ASTNode):
    """Условие if"""
    def __init__(self, condition):
        super().__init__()
        self.condition = condition
    
    def __repr__(self):
        return f"If(condition={self.condition})"

class VariableDeclarationNode(ASTNode):
    """Объявление переменной"""
    def __init__(self, name, type, value=None):
        super().__init__()
        self.name = name
        self.type = type
        self.value = value
    
    def __repr__(self):
        return f"VariableDeclaration(name={self.name}, type={self.type}, value={self.value})"

class AssignmentNode(ASTNode):
    """Присваивание"""
    def __init__(self, name, value):
        super().__init__()
        self.name = name
        self.value = value
    
    def __repr__(self):
        return f"Assignment(name={self.name}, value={self.value})"

class FunctionCallNode(ASTNode):
    """Вызов функции"""
    def __init__(self, name, args):
        super().__init__()
        self.name = name
        self.args = args
    
    def __repr__(self):
        return f"FunctionCall(name={self.name}, args={self.args})"

class BinaryOpNode(ASTNode):
    """Бинарная операция"""
    def __init__(self, left, op, right):
        super().__init__()
        self.left = left
        self.op = op
        self.right = right
    
    def __repr__(self):
        return f"BinaryOp({self.left} {self.op} {self.right})"

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = None
        self.advance()
        
        # Таблица символов
        self.symbols = {}
    
    def advance(self):
        """Переход к следующему токену"""
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
            self.pos += 1
        else:
            self.current_token = None
        return self.current_token
    
    def peek(self):
        """Просмотр следующего токена без продвижения"""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None
    
    def expect(self, token_type, error_msg=None):
        """Проверяет, что текущий токен имеет ожидаемый тип"""
        if self.current_token and self.current_token.type == token_type:
            token = self.current_token
            self.advance()
            return token
        
        if not error_msg:
            error_msg = f"Ожидался {token_type}, получен {self.current_token.type if self.current_token else 'EOF'}"
        raise SyntaxError(f"Строка {self.current_token.line}:{self.current_token.column} - {error_msg}")
    
    def parse(self):
        """Парсинг всей программы"""
        program = ProgramNode()
        
        # Парсим настройки (setup)
        while self.current_token and self.current_token.type != 'EOF':
            if self.current_token.type == 'PIN':
                node = self.parse_pin_declaration()
            elif self.current_token.type == 'FUNCTION':
                node = self.parse_function_declaration()
            elif self.current_token.type == 'LOOP':
                node = self.parse_loop()
            elif self.current_token.type == 'SERIAL_BEGIN':
                node = self.parse_serial_begin()
            elif self.current_token.type in ('INT', 'FLOAT', 'BOOL', 'CHAR', 'STRING'):
                node = self.parse_variable_declaration()
            elif self.current_token.type == 'ID' and self.peek() and self.peek().type == 'ASSIGN':
                node = self.parse_assignment()
            elif self.current_token.type in ('DIGITALWRITE', 'ANALOGWRITE', 'DELAY', 'PRINT', 'PRINTLN'):
                node = self.parse_function_call()
            else:
                self.advance()  # Пропускаем неизвестные токены
                continue
            
            program.add_child(node)
        
        return program
    
    def parse_pin_declaration(self):
        """Парсинг объявления пина"""
        self.expect('PIN')
        
        # Пин может быть числом или идентификатором
        if self.current_token.type in ('INTEGER', 'PIN_PREFIX', 'ID'):
            pin = self.current_token.value
            self.advance()
        else:
            raise SyntaxError("Ожидался номер пина")
        
        self.expect('ASSIGN')
        
        # Режим пина
        if self.current_token.type in ('OUTPUT', 'INPUT', 'INPUT_PULLUP'):
            mode = self.current_token.value
            self.advance()
        else:
            raise SyntaxError("Ожидался режим пина (выход, вход, вход_подтяжка)")
        
        value = None
        
        # Необязательное начальное значение
        if self.current_token and self.current_token.type == 'ASSIGN':
            self.advance()  # Пропускаем =
            if self.current_token.type in ('HIGH', 'LOW', 'INTEGER'):
                value = self.current_token.value
                self.advance()
        
        # Запоминаем пин в таблице символов
        self.symbols[pin] = {'type': 'pin', 'mode': mode}
        
        return PinDeclarationNode(pin, mode, value)
    
    def parse_function_call(self):
        """Парсинг вызова функции"""
        func_name = self.current_token.value
        self.advance()
        
        self.expect('LPAREN')
        args = []
        
        # Парсим аргументы
        while self.current_token and self.current_token.type != 'RPAREN':
            if self.current_token.type == 'ID':
                args.append(self.current_token.value)
            elif self.current_token.type in ('INTEGER', 'FLOAT', 'STRING'):
                args.append(self.current_token.value)
            elif self.current_token.type in ('HIGH', 'LOW'):
                args.append(self.current_token.value.upper())
            else:
                args.append(self.current_token.value)
            
            self.advance()
            
            if self.current_token and self.current_token.type == 'COMMA':
                self.advance()
        
        self.expect('RPAREN')
        
        # Создаем соответствующий узел
        if func_name == 'цифрзапись':
            if len(args) >= 2:
                return DigitalWriteNode(args[0], args[1])
        elif func_name == 'аналогзапись':
            if len(args) >= 2:
                return AnalogWriteNode(args[0], args[1])
        elif func_name == 'цифрчтение':
            if len(args) >= 1:
                return DigitalReadNode(args[0])
        elif func_name == 'аналогчтение':
            if len(args) >= 1:
                return AnalogReadNode(args[0])
        elif func_name == 'ждать':
            if len(args) >= 1:
                return DelayNode(args[0])
        elif func_name == 'печать':
            return SerialPrintNode(args[0] if args else "", newline=False)
        elif func_name == 'печать_строка':
            return SerialPrintNode(args[0] if args else "", newline=True)
        
        return FunctionCallNode(func_name, args)
    
    def parse_serial_begin(self):
        """Парсинг инициализации Serial"""
        self.expect('SERIAL_BEGIN')
        self.expect('LPAREN')
        
        baud_rate = self.current_token.value
        if self.current_token.type != 'INTEGER':
            raise SyntaxError("Ожидалась скорость передачи (целое число)")
        self.advance()
        
        self.expect('RPAREN')
        return SerialBeginNode(baud_rate)
    
    def parse_loop(self):
        """Парсинг основного цикла"""
        self.expect('LOOP')
        self.expect('COLON')
        
        loop_node = LoopNode()
        
        # Парсим содержимое цикла
        while self.current_token and self.current_token.type not in ('EOF', 'END'):
            if self.current_token.type == 'PIN':
                node = self.parse_pin_declaration()
            elif self.current_token.type in ('DIGITALWRITE', 'ANALOGWRITE', 'DELAY', 'PRINT', 'PRINTLN'):
                node = self.parse_function_call()
            elif self.current_token.type == 'IF':
                node = self.parse_if()
            elif self.current_token.type == 'WHILE':
                node = self.parse_while()
            elif self.current_token.type == 'FOR':
                node = self.parse_for()
            else:
                self.advance()
                continue
            
            loop_node.add_child(node)
        
        if self.current_token and self.current_token.type == 'END':
            self.advance()
        
        return loop_node
    
    def parse_if(self):
        """Парсинг условия if"""
        self.expect('IF')
        
        # Парсим условие
        condition = self.parse_expression()
        
        self.expect('COLON')
        
        if_node = IfNode(condition)
        
        # Парсим тело условия
        while self.current_token and self.current_token.type not in ('EOF', 'END', 'ELSE', 'ELIF'):
            if self.current_token.type in ('DIGITALWRITE', 'ANALOGWRITE', 'DELAY'):
                node = self.parse_function_call()
                if_node.add_child(node)
            else:
                self.advance()
        
        # Обработка else/elif
        if self.current_token and self.current_token.type in ('ELSE', 'ELIF'):
            self.advance()
            if self.current_token.type == 'COLON':
                self.advance()
                # Парсим else/elif блок
                while self.current_token and self.current_token.type not in ('EOF', 'END'):
                    if self.current_token.type in ('DIGITALWRITE', 'ANALOGWRITE', 'DELAY'):
                        node = self.parse_function_call()
                        if_node.add_child(node)
                    else:
                        self.advance()
        
        if self.current_token and self.current_token.type == 'END':
            self.advance()
        
        return if_node
    
    def parse_expression(self):
        """Парсинг выражения"""
        # Простая реализация для числовых и логических выражений
        if self.current_token.type in ('INTEGER', 'FLOAT', 'ID'):
            left = self.current_token.value
            self.advance()
            
            if self.current_token and self.current_token.type in ('EQ', 'NEQ', 'LT', 'LTE', 'GT', 'GTE'):
                op = self.current_token.type
                self.advance()
                
                if self.current_token.type in ('INTEGER', 'FLOAT', 'ID'):
                    right = self.current_token.value
                    self.advance()
                    return BinaryOpNode(left, op, right)
        
        return left
    
    def parse_variable_declaration(self):
        """Парсинг объявления переменной"""
        var_type = self.current_token.type
        self.advance()
        
        name = self.expect('ID').value
        
        value = None
        if self.current_token and self.current_token.type == 'ASSIGN':
            self.advance()
            if self.current_token.type in ('INTEGER', 'FLOAT', 'STRING', 'TRUE', 'FALSE'):
                value = self.current_token.value
                self.advance()
        
        # Запоминаем переменную в таблице символов
        self.symbols[name] = {'type': var_type, 'value': value}
        
        return VariableDeclarationNode(name, var_type, value)
    
    def parse_assignment(self):
        """Парсинг присваивания"""
        name = self.current_token.value
        self.advance()  # ID
        self.expect('ASSIGN')
        
        value = self.current_token.value
        self.advance()
        
        return AssignmentNode(name, value)
    
    def parse_while(self):
        """Парсинг цикла while"""
        # Упрощенная реализация
        self.expect('WHILE')
        condition = self.parse_expression()
        self.expect('COLON')
        
        while_node = LoopNode()  # Используем LoopNode для упрощения
        
        while self.current_token and self.current_token.type not in ('EOF', 'END'):
            if self.current_token.type in ('DIGITALWRITE', 'ANALOGWRITE', 'DELAY'):
                node = self.parse_function_call()
                while_node.add_child(node)
            else:
                self.advance()
        
        if self.current_token and self.current_token.type == 'END':
            self.advance()
        
        return while_node
    
    def parse_for(self):
        """Парсинг цикла for"""
        # Упрощенная реализация
        self.expect('FOR')
        self.expect('LPAREN')
        
        # Инициализация
        if self.current_token.type in ('INT', 'ID'):
            init = self.parse_variable_declaration() if self.current_token.type == 'INT' else self.parse_assignment()
        self.expect('SEMICOLON')
        
        # Условие
        condition = self.parse_expression()
        self.expect('SEMICOLON')
        
        # Инкремент
        if self.current_token.type == 'ID':
            increment = self.parse_assignment()
        self.expect('RPAREN')
        self.expect('COLON')
        
        for_node = LoopNode()
        
        # Тело цикла
        while self.current_token and self.current_token.type not in ('EOF', 'END'):
            if self.current_token.type in ('DIGITALWRITE', 'ANALOGWRITE', 'DELAY'):
                node = self.parse_function_call()
                for_node.add_child(node)
            else:
                self.advance()
        
        if self.current_token and self.current_token.type == 'END':
            self.advance()
        
        return for_node
    
    def parse_function_declaration(self):
        """Парсинг объявления функции"""
        self.expect('FUNCTION')
        name = self.expect('ID').value
        self.expect('LPAREN')
        
        # Параметры
        params = []
        while self.current_token and self.current_token.type != 'RPAREN':
            if self.current_token.type in ('INT', 'FLOAT', 'BOOL'):
                param_type = self.current_token.type
                self.advance()
                param_name = self.expect('ID').value
                params.append((param_type, param_name))
                
                if self.current_token and self.current_token.type == 'COMMA':
                    self.advance()
        
        self.expect('RPAREN')
        self.expect('COLON')
        
        # Запоминаем функцию в таблице символов
        self.symbols[name] = {'type': 'function', 'params': params}
        
        func_node = FunctionCallNode(name, [])
        
        # Тело функции
        while self.current_token and self.current_token.type not in ('EOF', 'END', 'RETURN'):
            if self.current_token.type in ('DIGITALWRITE', 'ANALOGWRITE', 'DELAY'):
                node = self.parse_function_call()
                func_node.add_child(node)
            else:
                self.advance()
        
        if self.current_token and self.current_token.type == 'RETURN':
            self.advance()
            # Обработка возвращаемого значения
            if self.current_token.type in ('INTEGER', 'FLOAT', 'ID'):
                self.advance()
        
        if self.current_token and self.current_token.type == 'END':
            self.advance()
        
        return func_node

if __name__ == "__main__":
    # Тестирование парсера
    test_code = """
    пин D13 = выход
    последовательный.начать(9600)
    
    цикл:
        цифрзапись(D13, высоко)
        ждать(1000)
        цифрзапись(D13, низко)
        ждать(500)
        печать("Светодиод мигнул")
    конец
    """
    
    lexer = Lexer(test_code)
    tokens = lexer.tokenize()
    
    parser = Parser(tokens)
    ast = parser.parse()
    
    print("AST:")
    for node in ast.children:
        print(f"  {node}")