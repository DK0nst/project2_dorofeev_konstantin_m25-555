
import shlex
import prompt
from .core import create_table, drop_table, list_tables, print_help
from .utils import load_metadata, save_metadata


def run():
    """
    Основной цикл программы для работы с базой данных.
    """
    print("***База данных***")
    print_help()
    
    while True:
        try:
            # Загружаем актуальные метаданные
            metadata = load_metadata()
            
            # Получаем команду от пользователя
            user_input = prompt.string("Введите команду: ")
            command_parts = shlex.split(user_input)
            
            if not command_parts:
                continue
            
            command = command_parts[0].lower()
            args = command_parts[1:]
            
            # Обработка команд
            if command == "exit":
                print("Выход из программы...")
                break
                
            elif command == "help":
                print_help()
                
            elif command == "create_table":
                if len(args) < 2:
                    print("Ошибка: Недостаточно аргументов. Используйте: create_table <имя_таблицы> <столбец1:тип> ...")
                    continue
                
                table_name = args[0]
                columns = args[1:]
                
                success, message = create_table(metadata, table_name, columns)
                print(message)
                
                if success:
                    save_metadata(metadata)
                    
            elif command == "drop_table":
                if len(args) != 1:
                    print("Ошибка: Неверное количество аргументов. Используйте: drop_table <имя_таблицы>")
                    continue
                
                table_name = args[0]
                success, message = drop_table(metadata, table_name)
                print(message)
                
                if success:
                    save_metadata(metadata)
                    
            elif command == "list_tables":
                result = list_tables(metadata)
                print(result)
                
            else:
                print(f"Функции '{command}' нет. Попробуйте снова или вызовите справку.")
                
        except KeyboardInterrupt:
            print("\nВыход из программы...")
            break
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            print("Попробуйте снова.")

def welcome():
    """Функция приветствия"""
    print("Первая попытка запустить проект!")
    print("***")
    
    while True:
        user_input = prompt.string("Введите команду: ")
        command = user_input.strip().lower()
        
        if command == "exit":
            print("Выход из программы...")
            break
        elif command == "help":
            print("<command> exit - выйти из программы")
            print("<command> help - справочная информация")
        elif command == "":
            continue  # Игнорируем пустые команды
        else:
            print(f"Неизвестная команда: {command}")
            print("Доступные команды: exit, help")