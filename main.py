#!/usr/bin/env python3
"""
Главная точка входа ArduinoScript
"""
import sys
import os
import argparse
from pathlib import Path

# Добавляем путь к src для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from compiler import ArduinoScriptCompiler, CLI
from lexer import Lexer
from parser import Parser
from codegen import CodeGenerator

def compile_file(input_file, output_file=None, verbose=False):
    """Компиляция одного файла"""
    compiler = ArduinoScriptCompiler()
    
    if verbose:
        print(f"🔧 Компиляция {input_file}...")
    
    success = compiler.compile_file(input_file, output_file)
    
    if success and verbose:
        valid, errors = compiler.validate()
        if errors:
            print("⚠ Предупреждения:")
            for error in errors:
                print(f"  - {error}")
    
    return success

def compile_project(project_dir, verbose=False):
    """Компиляция всего проекта"""
    project_dir = Path(project_dir)
    src_dir = project_dir / 'src'
    
    if not src_dir.exists():
        print(f"❌ Директория src не найдена в {project_dir}")
        return False
    
    success_count = 0
    fail_count = 0
    
    for file in src_dir.glob('*.arduino'):
        output_file = project_dir / f'{file.stem}.ino'
        
        if verbose:
            print(f"\n📄 Компиляция {file.name}...")
        
        if compile_file(file, output_file, verbose):
            success_count += 1
        else:
            fail_count += 1
    
    print(f"\n{'='*50}")
    print(f"📊 Результат компиляции проекта:")
    print(f"  ✅ Успешно: {success_count}")
    print(f"  ❌ С ошибками: {fail_count}")
    print(f"{'='*50}")
    
    return fail_count == 0

def interactive_shell():
    """Интерактивная оболочка ArduinoScript"""
    print("🚀 ArduinoScript Interactive Shell v1.0")
    print("Введите код на ArduinoScript. Для выхода введите 'выход' или 'exit'")
    print("Для получения справки введите 'помощь' или 'help'")
    
    compiler = ArduinoScriptCompiler()
    history = []
    
    while True:
        try:
            # Многострочный ввод
            print("\n" + "="*50)
            lines = []
            print("Введите код (пустая строка для выполнения):")
            
            while True:
                line = input(">>> " if not lines else "... ")
                
                if line.strip() == '' and lines:
                    break
                
                if line.strip().lower() in ('выход', 'exit', 'quit'):
                    print("Выход из оболочки...")
                    return
                
                if line.strip().lower() in ('помощь', 'help'):
                    show_interactive_help()
                    break
                
                if line.strip().lower() == 'история':
                    print("\nИстория команд:")
                    for i, cmd in enumerate(history[-10:], 1):
                        print(f"{i:2}. {cmd[:50]}...")
                    continue
                
                if line.strip().lower() == 'очистить':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    continue
                
                lines.append(line)
            
            if not lines:
                continue
            
            code = '\n'.join(lines)
            history.append(code)
            
            # Компиляция
            try:
                cpp_code = compiler.compile_string(code)
                print("\n✅ Скомпилировано успешно!")
                print("\n📋 Сгенерированный C++ код:")
                print("-" * 40)
                print(cpp_code)
                print("-" * 40)
                
                # Предлагаем сохранить
                save = input("\n💾 Сохранить в файл? (y/n): ").strip().lower()
                if save == 'y':
                    filename = input("Имя файла [output.ino]: ").strip()
                    if not filename:
                        filename = "output.ino"
                    
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(cpp_code)
                    print(f"✅ Файл сохранен: {filename}")
            
            except Exception as e:
                print(f"❌ Ошибка компиляции: {e}")
        
        except KeyboardInterrupt:
            print("\n\nВыход из оболочки...")
            break
        except EOFError:
            print("\nВыход из оболочки...")
            break

def show_interactive_help():
    """Показать справку для интерактивной оболочки"""
    help_text = """
📚 Справка по ArduinoScript Interactive Shell:

Основные команды:
  выход, exit, quit    - Выйти из оболочки
  помощь, help         - Показать эту справку
  история              - Показать историю команд
  очистить             - Очистить экран

Примеры кода:
  пин 13 = выход
  цикл:
      цифрзапись(13, высоко)
      ждать(1000)
      цифрзапись(13, низко)
      ждать(500)
  конец

Советы:
  - Вводите код построчно
  - Оставьте пустую строку для выполнения
  - Используйте русские ключевые слова
  - Поддерживаются все функции Arduino
"""
    print(help_text)

def run_tests():
    """Запуск тестов"""
    print("🧪 Запуск тестов...")
    
    test_dir = Path(__file__).parent / 'tests'
    if not test_dir.exists():
        print("❌ Директория tests не найдена")
        return False
    
    # Простые тесты без внешних зависимостей
    test_cases = [
        {
            'name': 'Мигание светодиодом',
            'code': '''пин 13 = выход
цикл:
    цифрзапись(13, высоко)
    ждать(1000)
    цифрзапись(13, низко)
    ждать(500)
конец''',
            'should_contain': ['pinMode(13, OUTPUT)', 'digitalWrite(13, HIGH)', 'delay(1000)']
        },
        {
            'name': 'Аналоговое чтение',
            'code': '''пин A0 = аналог
целое значение = 0
последовательный.начать(9600)

цикл:
    значение = аналогчтение(A0)
    печать_строка(значение)
    ждать(100)
конец''',
            'should_contain': ['analogRead(A0)', 'Serial.begin(9600)', 'Serial.println']
        }
    ]
    
    passed = 0
    failed = 0
    
    compiler = ArduinoScriptCompiler()
    
    for test in test_cases:
        print(f"\n📝 Тест: {test['name']}")
        print("-" * 40)
        
        try:
            result = compiler.compile_string(test['code'])
            
            # Проверяем наличие ожидаемых строк
            all_found = True
            for expected in test['should_contain']:
                if expected in result:
                    print(f"  ✅ Найдено: {expected}")
                else:
                    print(f"  ❌ Не найдено: {expected}")
                    all_found = False
            
            if all_found:
                print(f"✅ Тест пройден")
                passed += 1
            else:
                print(f"❌ Тест не пройден")
                failed += 1
        
        except Exception as e:
            print(f"❌ Ошибка компиляции: {e}")
            failed += 1
    
    print(f"\n{'='*40}")
    print(f"📊 Результаты тестирования:")
    print(f"  ✅ Пройдено: {passed}")
    print(f"  ❌ Не пройдено: {failed}")
    print(f"  📈 Успешность: {passed/(passed+failed)*100:.1f}%")
    print(f"{'='*40}")
    
    return failed == 0

def main():
    """Основная функция"""
    parser = argparse.ArgumentParser(
        description='ArduinoScript - Язык программирования для Arduino на русском',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Примеры:
  %(prog)s compile blink.arduino
  %(prog)s project MyProject
  %(prog)s shell
  %(prog)s test
        
Для получения дополнительной информации:
  https://github.com/arduinoscript/arduinoscript
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Команда')
    
    # Команда compile
    compile_parser = subparsers.add_parser('compile', help='Компиляция файла')
    compile_parser.add_argument('input', help='Входной файл .arduino')
    compile_parser.add_argument('-o', '--output', help='Выходной файл .ino')
    compile_parser.add_argument('-v', '--verbose', action='store_true', help='Подробный вывод')
    
    # Команда project
    project_parser = subparsers.add_parser('project', help='Управление проектами')
    project_parser.add_argument('action', choices=['new', 'build', 'clean'], 
                               help='Действие: new, build, clean')
    project_parser.add_argument('name', nargs='?', help='Имя проекта')
    project_parser.add_argument('-v', '--verbose', action='store_true', help='Подробный вывод')
    
    # Команда shell
    subparsers.add_parser('shell', help='Интерактивная оболочка')
    
    # Команда test
    subparsers.add_parser('test', help='Запуск тестов')
    
    # Команда version
    subparsers.add_parser('version', help='Показать версию')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'compile':
        success = compile_file(args.input, args.output, args.verbose)
        sys.exit(0 if success else 1)
    
    elif args.command == 'project':
        if args.action == 'new':
            if not args.name:
                print("❌ Укажите имя проекта")
                sys.exit(1)
            CLI.create_project(args.name)
        
        elif args.action == 'build':
            project_dir = args.name if args.name else '.'
            success = compile_project(project_dir, args.verbose)
            sys.exit(0 if success else 1)
        
        elif args.action == 'clean':
            project_dir = Path(args.name if args.name else '.')
            # Удаляем скомпилированные файлы
            for ino_file in project_dir.glob('*.ino'):
                ino_file.unlink()
                print(f"🗑️ Удален: {ino_file}")
            print("✅ Очистка завершена")
    
    elif args.command == 'shell':
        interactive_shell()
    
    elif args.command == 'test':
        success = run_tests()
        sys.exit(0 if success else 1)
    
    elif args.command == 'version':
        print("ArduinoScript Compiler v1.0.0")
        print("Язык программирования для Arduino")
        print("© 2024 ArduinoScript Team")
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
