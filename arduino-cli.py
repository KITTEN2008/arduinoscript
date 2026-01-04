#!/usr/bin/env python3
"""
Интеграция с Arduino CLI для загрузки скетчей
"""
import subprocess
import sys
import os
import json
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
import shutil

class ArduinoCLI:
    """Класс для работы с Arduino CLI"""
    
    def __init__(self, cli_path: str = None):
        """
        Инициализация Arduino CLI
        
        Args:
            cli_path: Путь к arduino-cli (если None, ищет в PATH)
        """
        self.cli_path = cli_path or 'arduino-cli'
        self.version = self._get_version()
        
        if not self.version:
            print("❌ Arduino CLI не найден!")
            print("📥 Установите его: https://arduino.github.io/arduino-cli/installation/")
            sys.exit(1)
    
    def _get_version(self) -> Optional[str]:
        """Получить версию Arduino CLI"""
        try:
            result = subprocess.run(
                [self.cli_path, 'version', '--format', 'json'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return data.get('VersionString', 'unknown')
        
        except (subprocess.SubprocessError, json.JSONDecodeError, FileNotFoundError):
            pass
        
        return None
    
    def is_installed(self) -> bool:
        """Проверка установки Arduino CLI"""
        return self.version is not None
    
    def list_boards(self) -> List[Dict[str, Any]]:
        """Список подключенных плат"""
        try:
            result = subprocess.run(
                [self.cli_path, 'board', 'list', '--format', 'json'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return data
            
        except (subprocess.SubprocessError, json.JSONDecodeError):
            pass
        
        return []
    
    def detect_board(self) -> Optional[Dict[str, Any]]:
        """Автоматическое определение подключенной платы"""
        boards = self.list_boards()
        
        if not boards:
            return None
        
        # Ищем первую подключенную плату
        for board in boards:
            if board.get('boards'):
                for b in board['boards']:
                    if b.get('fqbn'):
                        return {
                            'port': board.get('address'),
                            'fqbn': b.get('fqbn'),
                            'name': b.get('name', 'Unknown')
                        }
        
        return None
    
    def get_fqbn(self, board_type: str = 'uno') -> Optional[str]:
        """Получить FQBN для типа платы"""
        fqbn_map = {
            'uno': 'arduino:avr:uno',
            'nano': 'arduino:avr:nano',
            'mega': 'arduino:avr:mega',
            'leonardo': 'arduino:avr:leonardo',
            'micro': 'arduino:avr:micro',
            'due': 'arduino:sam:arduino_due_x',
            'mkr1000': 'arduino:samd:mkr1000',
            'esp8266': 'esp8266:esp8266:nodemcuv2',
            'esp32': 'esp32:esp32:esp32',
        }
        
        return fqbn_map.get(board_type.lower())
    
    def compile_sketch(self, sketch_path: str, fqbn: str = None, 
                      verbose: bool = False) -> bool:
        """
        Компиляция скетча
        
        Args:
            sketch_path: Путь к файлу .ino
            fqbn: FQBN платы (если None, пробуем определить автоматически)
            verbose: Подробный вывод
        
        Returns:
            Успешность компиляции
        """
        sketch_path = Path(sketch_path)
        
        if not sketch_path.exists():
            print(f"❌ Файл не найден: {sketch_path}")
            return False
        
        if fqbn is None:
            board_info = self.detect_board()
            if board_info and board_info.get('fqbn'):
                fqbn = board_info['fqbn']
            else:
                fqbn = 'arduino:avr:uno'  # По умолчанию Arduino Uno
        
        print(f"🔧 Компиляция {sketch_path.name} для {fqbn}...")
        
        cmd = [self.cli_path, 'compile', '--fqbn', fqbn, str(sketch_path.parent)]
        
        if verbose:
            cmd.append('-v')
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60  # 60 секунд на компиляцию
            )
            
            if result.returncode == 0:
                print("✅ Компиляция успешна!")
                if verbose and result.stdout:
                    print("\nВывод компилятора:")
                    print(result.stdout[:1000])  # Первые 1000 символов
                return True
            else:
                print("❌ Ошибка компиляции:")
                if result.stderr:
                    print(result.stderr)
                elif result.stdout:
                    # Иногда ошибки выводятся в stdout
                    error_lines = [line for line in result.stdout.split('\n') 
                                 if 'error' in line.lower()]
                    if error_lines:
                        print("\n".join(error_lines[:10]))
                return False
        
        except subprocess.TimeoutExpired:
            print("❌ Таймаут компиляции (60 секунд)")
            return False
        except Exception as e:
            print(f"❌ Неизвестная ошибка: {e}")
            return False
    
    def upload_sketch(self, sketch_path: str, port: str = None, 
                     fqbn: str = None, verbose: bool = False) -> bool:
        """
        Загрузка скетча на плату
        
        Args:
            sketch_path: Путь к файлу .ino
            port: COM порт (если None, пробуем определить автоматически)
            fqbn: FQBN платы (если None, пробуем определить автоматически)
            verbose: Подробный вывод
        
        Returns:
            Успешность загрузки
        """
        sketch_path = Path(sketch_path)
        
        if not sketch_path.exists():
            print(f"❌ Файл не найден: {sketch_path}")
            return False
        
        # Определяем порт
        if port is None:
            board_info = self.detect_board()
            if board_info and board_info.get('port'):
                port = board_info['port']
            else:
                print("❌ Не удалось определить порт Arduino")
                print("📋 Подключенные платы:")
                self.print_board_list()
                return False
        
        # Определяем FQBN
        if fqbn is None:
            if board_info and board_info.get('fqbn'):
                fqbn = board_info['fqbn']
            else:
                fqbn = 'arduino:avr:uno'
        
        print(f"🚀 Загрузка {sketch_path.name} на {port} ({fqbn})...")
        
        cmd = [
            self.cli_path, 'upload',
            '-p', port,
            '--fqbn', fqbn,
            str(sketch_path.parent)
        ]
        
        if verbose:
            cmd.append('-v')
        
        try:
            # Сначала компилируем
            if not self.compile_sketch(sketch_path, fqbn, verbose):
                return False
            
            print(f"📤 Загрузка на порт {port}...")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # 120 секунд на загрузку
            )
            
            if result.returncode == 0:
                print("✅ Загрузка успешна!")
                return True
            else:
                print("❌ Ошибка загрузки:")
                if result.stderr:
                    print(result.stderr)
                return False
        
        except subprocess.TimeoutExpired:
            print("❌ Таймаут загрузки (120 секунд)")
            return False
        except Exception as e:
            print(f"❌ Неизвестная ошибка: {e}")
            return False
    
    def print_board_list(self):
        """Вывод списка подключенных плат"""
        boards = self.list_boards()
        
        if not boards:
            print("📭 Нет подключенных плат")
            return
        
        print("📋 Подключенные платы:")
        print("-" * 60)
        
        for board_info in boards:
            address = board_info.get('address', 'N/A')
            protocol = board_info.get('protocol', 'N/A')
            protocol_label = board_info.get('protocol_label', 'N/A')
            
            print(f"📍 Порт: {address}")
            print(f"   Протокол: {protocol} ({protocol_label})")
            
            if board_info.get('boards'):
                for board in board_info['boards']:
                    name = board.get('name', 'Unknown')
                    fqbn = board.get('fqbn', 'N/A')
                    print(f"   Плата: {name}")
                    print(f"   FQBN: {fqbn}")
            
            print("-" * 60)
    
    def install_core(self, core: str, verbose: bool = False):
        """Установка ядра платы"""
        print(f"📦 Установка ядра: {core}...")
        
        cmd = [self.cli_path, 'core', 'install', core]
        
        if verbose:
            cmd.append('-v')
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 минут на установку
            )
            
            if result.returncode == 0:
                print(f"✅ Ядро {core} установлено")
                return True
            else:
                print(f"❌ Ошибка установки ядра {core}:")
                if result.stderr:
                    print(result.stderr)
                return False
        
        except subprocess.TimeoutExpired:
            print(f"❌ Таймаут установки ядра {core}")
            return False
    
    def install_library(self, library: str, verbose: bool = False):
        """Установка библиотеки"""
        print(f"📚 Установка библиотеки: {library}...")
        
        cmd = [self.cli_path, 'lib', 'install', library]
        
        if verbose:
            cmd.append('-v')
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # 2 минуты на установку
            )
            
            if result.returncode == 0:
                print(f"✅ Библиотека {library} установлена")
                return True
            else:
                print(f"❌ Ошибка установки библиотеки {library}:")
                if result.stderr:
                    print(result.stderr)
                return False
        
        except subprocess.TimeoutExpired:
            print(f"❌ Таймаут установки библиотеки {library}")
            return False
    
    def create_project(self, project_name: str, board_type: str = 'uno'):
        """Создание нового проекта Arduino"""
        project_dir = Path(project_name)
        
        if project_dir.exists():
            print(f"❌ Директория {project_name} уже существует")
            return False
        
        # Создаем структуру проекта
        project_dir.mkdir()
        (project_dir / 'src').mkdir()
        (project_dir / 'lib').mkdir()
        (project_dir / 'hardware').mkdir()
        
        # Основной файл ArduinoScript
        main_file = project_dir / 'src' / f'{project_name}.arduino'
        
        # Получаем FQBN
        fqbn = self.get_fqbn(board_type)
        
        template = f"""// Проект: {project_name}
// Плата: {board_type.upper()}
// FQBN: {fqbn}

пин светодиод = выход
целое интервал = 1000

последовательный.начать(9600)
печать_строка("Проект {project_name} запущен")

цикл:
    цифрзапись(светодиод, высоко)
    печать("Светодиод ВКЛ")
    ждать(интервал)
    
    цифрзапись(светодиод, низко)
    печать_строка("Светодиод ВЫКЛ")
    ждать(интервал)
конец
"""
        
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(template)
        
        # Файл конфигурации
        config = {
            'project': project_name,
            'board': board_type,
            'fqbn': fqbn,
            'version': '1.0.0',
            'author': 'ArduinoScript'
        }
        
        config_file = project_dir / 'arduinoscript.json'
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        # README
        readme = f"""# {project_name}

Проект Arduino созданный с помощью ArduinoScript.

## Структура

- `src/` - Исходные коды на ArduinoScript
- `lib/` - Библиотеки Arduino
- `hardware/` - Пользовательские платы

## Компиляция и загрузка

```bash
# Компиляция
arduinoscript compile src/{project_name}.arduino

# Загрузка на плату
arduino-cli upload -p [PORT] --fqbn {fqbn} .
