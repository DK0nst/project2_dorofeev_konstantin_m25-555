import shlex
import prompt
from .utils import load_metadata, save_metadata
from .core import create_table, drop_table, list_tables

def print_help():
    print()
    print(50*"=")
    print("Справка")
    print(50*"=")

    print("create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("list_tables - показать список всех таблиц")
    print("drop_table <имя_таблицы> - удалить таблицу")

    print()
    print("exit - выйти из программы")
    print("help - справочная информация")  

    print(50*"=")

def run():

    """
    Загружает актуальные метаданные.
    Запрашивает ввод у пользователя.
    Разбирает введенную строку на команду и аргументы.
    После каждой успешной операции (create_table, drop_table) сохраняйте измененные метаданные с помощью save_metadata.
    """

    print_help()

    while True:
        try:
            # Загружаем актуальные метаданные
            metadata = load_metadata()


            # Получаем команду от пользователя
            user_input = prompt.string("\nВведите команду: ")
            command_parts = shlex.split(user_input)
            
            if not command_parts:
                continue
            
            command = command_parts[0].lower()
            args = command_parts[1:]


            if command == "exit":
                print("\nВыход из программы...")
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
                continue
                
        except KeyboardInterrupt:
            print("\nВыход из программы...")
            break
        except EOFError:
            print("\nВыход из программы...")
            break