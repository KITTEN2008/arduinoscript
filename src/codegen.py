"""
Генератор C++ кода для Arduino
"""
from keywords import KEYWORDS, PIN_ALIASES, ARDUINO_FUNCTIONS

class CodeGenerator:
    def __init__(self, ast):
        self.ast = ast
        self.output = []
        self.indent_level = 0
        self.variables = {}
        self.in_setup = True
        self.includes = set(['<Arduino.h>'])
    
    def generate(self):
        """Генерация всего кода"""
        self.generate_header()
        self.generate_setup()
        self.generate_loop()
        return '\n'.join(self.output)
    
    def generate_header(self):
        """Генерация заголовка файла"""
        self.output.append("// Сгенерировано ArduinoScript")
        self.output.append("// Автоматически созданный код")
        self.output.append("")
        
        # Добавляем необходимые заголовочные файлы
        for include in sorted(self.includes):
            self.output.append(f"#include {include}")
        
        self.output.append("")
        
        # Объявляем глобальные переменные
        if self.variables:
            self.output.append("// Глобальные переменные")
            for var_name, var_info in self.variables.items():
                if var_info['type'] == 'pin':
                    continue  # Пины объявляются в setup
                
                c_type = self.map_type(var_info['type'])
                value = var_info.get('value', '')
                if value is not None:
                    if var_info['type'] == 'STRING':
                        self.output.append(f'{c_type} {var_name} = "{value}";')
                    elif var_info['type'] == 'BOOL':
                        bool_val = 'true' if value else 'false'
                        self.output.append(f'{c_type} {var_name} = {bool_val};')
                    else:
                        self.output.append(f'{c_type} {var_name} = {value};')
                else:
                    self.output.append(f'{c_type} {var_name};')
            self.output.append("")
    
    def generate_setup(self):
        """Генерация функции setup()"""
        self.output.append("void setup() {")
        self.indent_level += 1
        
        # Проходим по всем узлам AST
        for node in self.ast.children:
            self.generate_node(node, in_setup=True)
        
        self.indent_level -= 1
        self.output.append("}")
        self.output.append("")
        
        # Переключаемся в режим генерации loop
        self.in_setup = False
    
    def generate_loop(self):
        """Генерация функции loop()"""
        self.output.append("void loop() {")
        self.indent_level += 1
        
        # Ищем основной цикл программы
        for node in self.ast.children:
            if node.__class__.__name__ == 'LoopNode':
                self.generate_node(node, in_setup=False)
                break
        
        self.indent_level -= 1
        self.output.append("}")
    
    def generate_node(self, node, in_setup=True):
        """Генерация кода для узла AST"""
        indent = "  " * self.indent_level
        
        if node.__class__.__name__ == 'PinDeclarationNode':
            self.generate_pin_declaration(node, indent)
        
        elif node.__class__.__name__ == 'DigitalWriteNode':
            self.generate_digital_write(node, indent)
        
        elif node.__class__.__name__ == 'AnalogWriteNode':
            self.generate_analog_write(node, indent)
        
        elif node.__class__.__name__ == 'DigitalReadNode':
            self.generate_digital_read(node, indent)
        
        elif node.__class__.__name__ == 'AnalogReadNode':
            self.generate_analog_read(node, indent)
        
        elif node.__class__.__name__ == 'DelayNode':
            self.generate_delay(node, indent)
        
        elif node.__class__.__name__ == 'SerialBeginNode':
            self.generate_serial_begin(node, indent)
        
        elif node.__class__.__name__ == 'SerialPrintNode':
            self.generate_serial_print(node, indent)
        
        elif node.__class__.__name__ == 'LoopNode':
            self.generate_loop_content(node, indent)
        
        elif node.__class__.__name__ == 'IfNode':
            self.generate_if(node, indent)
        
        elif node.__class__.__name__ == 'VariableDeclarationNode':
            self.generate_variable_declaration(node, indent)
        
        elif node.__class__.__name__ == 'AssignmentNode':
            self.generate_assignment(node, indent)
        
        elif node.__class__.__name__ == 'FunctionCallNode':
            self.generate_function_call(node, indent)
        
        elif node.__class__.__name__ == 'BinaryOpNode':
            self.generate_binary_op(node, indent)
    
    def generate_pin_declaration(self, node, indent):
        """Генерация кода для объявления пина"""
        pin = self.normalize_pin(node.pin)
        mode_map = {
            'выход': 'OUTPUT',
            'вход': 'INPUT',
            'вход_подтяжка': 'INPUT_PULLUP',
            'аналог': 'INPUT',
            'шим': 'OUTPUT'
        }
        
        mode = mode_map.get(node.mode, 'OUTPUT')
        
        self.output.append(f'{indent}pinMode({pin}, {mode});')
        
        if node.value is not None:
            value_map = {
                'высоко': 'HIGH',
                'низко': 'LOW',
                'включено': 'HIGH',
                'выключено': 'LOW'
            }
            
            value = value_map.get(str(node.value).lower(), node.value)
            
            if mode == 'OUTPUT':
                self.output.append(f'{indent}digitalWrite({pin}, {value});')
            elif mode == 'INPUT_PULLUP':
                # Для подтяжки к питанию
                pass
    
    def generate_digital_write(self, node, indent):
        """Генерация digitalWrite"""
        pin = self.normalize_pin(node.pin)
        value = self.normalize_value(node.value)
        self.output.append(f'{indent}digitalWrite({pin}, {value});')
    
    def generate_analog_write(self, node, indent):
        """Генерация analogWrite (PWM)"""
        pin = self.normalize_pin(node.pin)
        value = node.value
        self.output.append(f'{indent}analogWrite({pin}, {value});')
    
    def generate_digital_read(self, node, indent):
        """Генерация digitalRead"""
        pin = self.normalize_pin(node.pin)
        self.output.append(f'{indent}digitalRead({pin});')
    
    def generate_analog_read(self, node, indent):
        """Генерация analogRead"""
        pin = self.normalize_pin(node.pin)
        if not pin.startswith('A'):
            pin = f'A{pin}' if pin.isdigit() else pin
        self.output.append(f'{indent}analogRead({pin});')
    
    def generate_delay(self, node, indent):
        """Генерация delay"""
        duration = node.duration
        self.output.append(f'{indent}delay({duration});')
    
    def generate_serial_begin(self, node, indent):
        """Генерация Serial.begin"""
        baud_rate = node.baud_rate
        self.output.append(f'{indent}Serial.begin({baud_rate});')
        self.includes.add('<SoftwareSerial.h>')
    
    def generate_serial_print(self, node, indent):
        """Генерация Serial.print/println"""
        value = node.value
        if node.newline:
            self.output.append(f'{indent}Serial.println({value});')
        else:
            self.output.append(f'{indent}Serial.print({value});')
    
    def generate_loop_content(self, node, indent):
        """Генерация содержимого цикла"""
        for child in node.children:
            self.generate_node(child, in_setup=False)
    
    def generate_if(self, node, indent):
        """Генерация условия if"""
        condition = self.generate_expression(node.condition)
        self.output.append(f'{indent}if ({condition}) {{')
        self.indent_level += 1
        
        for child in node.children:
            self.generate_node(child, in_setup=False)
        
        self.indent_level -= 1
        self.output.append(f'{indent}}}')
    
    def generate_variable_declaration(self, node, indent):
        """Генерация объявления переменной"""
        c_type = self.map_type(node.type)
        
        if node.value is not None:
            value = self.normalize_value(node.value, node.type)
            self.output.append(f'{indent}{c_type} {node.name} = {value};')
        else:
            self.output.append(f'{indent}{c_type} {node.name};')
        
        # Запоминаем переменную
        self.variables[node.name] = {'type': node.type, 'value': node.value}
    
    def generate_assignment(self, node, indent):
        """Генерация присваивания"""
        value = self.normalize_value(node.value)
        self.output.append(f'{indent}{node.name} = {value};')
    
    def generate_function_call(self, node, indent):
        """Генерация вызова функции"""
        args = ', '.join(str(arg) for arg in node.args)
        self.output.append(f'{indent}{node.name}({args});')
    
    def generate_binary_op(self, node, indent):
        """Генерация бинарной операции"""
        op_map = {
            'EQ': '==',
            'NEQ': '!=',
            'LT': '<',
            'LTE': '<=',
            'GT': '>',
            'GTE': '>=',
            'AND': '&&',
            'OR': '||'
        }
        
        op = op_map.get(node.op, node.op)
        left = node.left
        right = self.normalize_value(node.right)
        
        return f'{left} {op} {right}'
    
    def generate_expression(self, expr):
        """Генерация выражения"""
        if isinstance(expr, BinaryOpNode):
            return self.generate_binary_op(expr, "")
        elif isinstance(expr, str):
            return self.normalize_value(expr)
        else:
            return str(expr)
    
    def normalize_pin(self, pin):
        """Нормализация номера пина"""
        if isinstance(pin, str):
            # Замена алиасов
            if pin in PIN_ALIASES:
                pin = PIN_ALIASES[pin]
            
            # Преобразование D13 в 13, A0 в A0
            if pin.startswith('D'):
                return pin[1:]
            elif pin.upper().startswith('A'):
                return pin.upper()
        
        return str(pin)
    
    def normalize_value(self, value, var_type=None):
        """Нормализация значений"""
        if isinstance(value, str):
            value_lower = value.lower()
            
            # Логические значения
            if value_lower in ('истина', 'true', 'высоко', 'включено'):
                return 'HIGH' if var_type == 'pin' else 'true'
            elif value_lower in ('ложь', 'false', 'низко', 'выключено'):
                return 'LOW' if var_type == 'pin' else 'false'
            
            # Проверяем, является ли это именем пина
            if value in PIN_ALIASES:
                return self.normalize_pin(PIN_ALIASES[value])
            
            # Обработка строк
            if var_type == 'STRING' and not (value.startswith('"') and value.endswith('"')):
                return f'"{value}"'
        
        return str(value)
    
    def map_type(self, type_name):
        """Преобразование типов ArduinoScript в типы C++"""
        type_map = {
            'INT': 'int',
            'FLOAT': 'float',
            'BOOL': 'bool',
            'CHAR': 'char',
            'STRING': 'String',
            'VOID': 'void',
            'LONG': 'long',
            'BYTE': 'byte',
            'WORD': 'word'
        }
        return type_map.get(type_name, 'int')

if __name__ == "__main__":
    # Тестирование генератора кода
    from parser import Parser, PinDeclarationNode, DigitalWriteNode, DelayNode, LoopNode
    
    # Создаем простой AST
    ast = Parser([])
    ast.children = [
        PinDeclarationNode('D13', 'выход'),
        LoopNode()
    ]
    
    loop_node = ast.children[1]
    loop_node.children = [
        DigitalWriteNode('D13', 'высоко'),
        DelayNode(1000),
        DigitalWriteNode('D13', 'низко'),
        DelayNode(500)
    ]
    
    generator = CodeGenerator(ast)
    cpp_code = generator.generate()
    print(cpp_code)