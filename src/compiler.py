"""
Главный компилятор ArduinoScript
"""
import os
import sys
from pathlib import Path
from lexer import Lexer
from parser import Parser
from codegen import CodeGenerator

class ArduinoScriptCompiler:
    def __init__(self, source_path=None):
        self.source_path = source_path
        self.source_code = ""
        self.ast = None
        self.cpp_code = ""
        
    def compile_file(self, input_path, output_path=None):
        """Компиляция файла"""
        try:
            # Чтение исходного кода
            with open(input_path, 'r', encoding='utf-8') as f:
                self.source_code = f.read()
            
            # Определение пути вывода
            if output_path is None:
                output_path = Path(input_path).with_suffix('.ino')
            
            # Компиляция
            self.compile(self.source_code)
            
            # Запись результата
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(self.cpp_code)
            
            print(f"✓ Успешно скомпилировано: {input_path}")
            print(f"✓ Сгенерирован файл: {output_path}")
            
            return True
            
        except Exception as e:
            print(f"✗ Ошибка компиляции: {e}")
            return False
    
    def compile(self, source_code):
        """Основная процедура компиляции"""
        # Лексический анализ
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        
        # Синтаксический анализ
        parser = Parser(tokens)
        self.ast = parser.parse()
        
        # Генерация кода
        generator = CodeGenerator(self.ast)
        self.cpp_code = generator.generate()
        
        return self.cpp_code
    
    def compile_string(self, source_code):
        """Компиляция строки с кодом"""
        return self.compile(source_code)
    
    def validate(self):
        """Проверка валидности скомпилированного кода"""
        required_functions = ['setup', 'loop']
        errors = []
        
        lines = self.cpp_code.split('\n')
        
        # Проверяем наличие setup и loop
        has_setup = any('void setup()' in line for line in lines)
        has_loop = any('void loop()' in line for line in lines)
        
        if not has_setup:
            errors.append("Отсутствует функция setup()")
        if not has_loop:
            errors.append("Отсутствует функция loop()")
        
        # Проверяем синтаксис C++
        # (можно добавить вызов внешнего компилятора Arduino)
        
        return len(errors) == 0, errors

class CLI:
    """Командный интерфейс компилятора"""
    
    @staticmethod
    def main():
        if len(sys.argv) < 2:
            print("Использование: arduinoscript <команда> [аргументы]")
            print("\nКоманды:")
            print("  compile <файл.arduino> [файл.ino]  - Компиляция файла")
            print("  run <файл.arduino>                - Компиляция и запуск через Arduino CLI")
            print("  new <проект>                      - Создание нового проекта")
            print("  help                              - Показать справку")
            return
        
        command = sys.argv[1]
        compiler = ArduinoScriptCompiler()
        
        if command == 'compile':
            if len(sys.argv) < 3:
                print("Укажите файл для компиляции")
                return
            
            input_file = sys.argv[2]
            output_file = sys.argv[3] if len(sys.argv) > 3 else None
            
            if not os.path.exists(input_file):
                print(f"Файл не найден: {input_file}")
                return
            
            compiler.compile_file(input_file, output_file)
            
            # Валидация
            valid, errors = compiler.validate()
            if not valid:
                print("Предупреждения:")
                for error in errors:
                    print(f"  ⚠ {error}")
        
        elif command == 'run':
            if len(sys.argv) < 3:
                print("Укажите файл для запуска")
                return
            
            input_file = sys.argv[2]
            
            # Компиляция
            success = compiler.compile_file(input_file)
            if not success:
                return
            
            # Попытка загрузки через Arduino CLI
            output_file = Path(input_file).with_suffix('.ino')
            CLI.upload_to_arduino(output_file)
        
        elif command == 'new':
            if len(sys.argv) < 3:
                print("Укажите имя проекта")
                return
            
            project_name = sys.argv[2]
            CLI.create_project(project_name)
        
        elif command == 'help':
            CLI.show_help()
        
        else:
            print(f"Неизвестная команда: {command}")
            print("Используйте 'arduinoscript help' для справки")
    
    @staticmethod
    def upload_to_arduino(ino_file):
        """Загрузка кода на Arduino"""
        import subprocess
        
        print(f"\n🔄 Попытка загрузки на Arduino...")
        
        try:
            # Проверяем наличие arduino-cli
            result = subprocess.run(['arduino-cli', '--version'], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                print("❌ Arduino CLI не установлен")
                print("Установите его с https://arduino.github.io/arduino-cli/")
                return
            
            # Компиляция
            print("⚙ Компиляция проекта...")
            compile_cmd = [
                'arduino-cli', 'compile',
                '--fqbn', 'arduino:avr:uno',
                str(ino_file)
            ]
            
            result = subprocess.run(compile_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Ошибка компиляции:\n{result.stderr}")
                return
            
            # Поиск подключенных плат
            print("🔍 Поиск подключенных плат...")
            board_cmd = ['arduino-cli', 'board', 'list']
            result = subprocess.run(board_cmd, capture_output=True, text=True)
            
            if 'tty' not in result.stdout and 'COM' not in result.stdout:
                print("❌ Arduino не найден")
                print("Подключите плату и проверьте порт")
                return
            
            # Загрузка (нужно указать порт вручную)
            print("📤 Для загрузки выполните команду:")
            print(f"arduino-cli upload -p /dev/ttyUSB0 --fqbn arduino:avr:uno {ino_file}")
            print("\nЗамените /dev/ttyUSB0 на ваш порт (COM3 для Windows)")
        
        except FileNotFoundError:
            print("❌ Arduino CLI не найден")
            print("Установите его с https://arduino.github.io/arduino-cli/")
    
    @staticmethod
    def create_project(project_name):
        """Создание нового проекта"""
        import shutil
        
        project_dir = Path(project_name)
        
        if project_dir.exists():
            print(f"❌ Директория {project_name} уже существует")
            return
        
        # Создаем структуру проекта
        project_dir.mkdir()
        (project_dir / 'src').mkdir()
        (project_dir / 'examples').mkdir()
        (project_dir / 'lib').mkdir()
        
        # Создаем основной файл
        main_file = project_dir / 'src' / f'{project_name}.arduino'
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(f"""// Проект: {project_name}
// Создан ArduinoScript

пин светодиод = выход

цикл:
    цифрзапись(светодиод, высоко)
    ждать(1000)
    цифрзапись(светодиод, низко)
    ждать(500)
конец
""")
        
        # Создаем README
        readme = project_dir / 'README.md'
        with open(readme, 'w', encoding='utf-8') as f:
            f.write(f"""# {project_name}

Проект Arduino, созданный с помощью ArduinoScript.

## Компиляция

```bash
cd {project_name}
arduinoscript compile src/{project_name}.arduino
