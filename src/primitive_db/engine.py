import shlex
import prompt
from .core import (
    create_table, drop_table, list_tables, print_help,
    insert, select, update, delete, info, display_table
)
from .utils import load_metadata, save_metadata

def parse_value(value_str):
    """Парсит строковое значение в соответствующий тип"""
    value_str = value_str.strip()
    
    # Булевы значения
    if value_str.lower() in ('true', 'false'):
        return value_str.lower() == 'true'
    
    # Числа
    if value_str.isdigit() or (value_str[0] == '-' and value_str[1:].isdigit()):
        return int(value_str)
    
    # Строки (убираем кавычки если есть)
    if (value_str.startswith('"') and value_str.endswith('"')) or \
       (value_str.startswith("'") and value_str.endswith("'")):
        return value_str[1:-1]
    
    return value_str

def parse_where_condition(where_str):
    """
    Парсит условие WHERE в формате "столбец=значение"
    Возвращает словарь {столбец: значение}
    """
    if "=" not in where_str:
        return None, 'Неверный формат условия WHERE. Ожидается: "столбец=значение"'
    
    parts = where_str.split("=", 1)
    column = parts[0].strip()
    value_str = parts[1].strip()
    
    # Парсим значение
    value = parse_value(value_str)
    
    return {column: value}, None

def parse_set_clause(set_str):
    """
    Парсит SET выражение в формате "столбец=значение"
    Возвращает словарь {столбец: значение}
    """
    if "=" not in set_str:
        return None, 'Неверный формат SET. Ожидается: "столбец=значение"'
    
    parts = set_str.split("=", 1)
    column = parts[0].strip()
    value_str = parts[1].strip()
    
    value = parse_value(value_str)
    
    return {column: value}, None

def parse_values_list(values_str):
    """Парсит список значений в формате (value1, value2, value3)"""
    # Убираем скобки если есть
    if values_str.startswith("(") and values_str.endswith(")"):
        values_str = values_str[1:-1]
    
    # Простой парсинг - разбиваем по запятым
    values = []
    current_value = ""
    in_quotes = False
    quote_char = None
    
    for char in values_str:
        if char in ('"', "'") and not in_quotes:
            in_quotes = True
            quote_char = char
            current_value += char
        elif char == quote_char and in_quotes:
            in_quotes = False
            current_value += char
            values.append(current_value.strip())
            current_value = ""
        elif char == "," and not in_quotes:
            if current_value.strip():
                values.append(current_value.strip())
            current_value = ""
        else:
            current_value += char
    
    if current_value.strip():
        values.append(current_value.strip())
    
    # Парсим значения
    return [parse_value(val) for val in values if val.strip()]

def run():
    """
    Основной цикл программы для работы с базой данных.
    """
    print("***Операции с данными***")
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

            # ========== CRUD КОМАНДЫ ==========
                
            elif command == "insert" and len(args) >= 4 and args[0] == "into" and args[2] == "values":
                # insert into users values ("John", 25, true)
                table_name = args[1]
                values_str = " ".join(args[3:])
                values = parse_values_list(values_str)
                
                success, message = insert(metadata, table_name, values)
                print(message)
                
            elif command == "select" and len(args) >= 2 and args[0] == "from":
                # select from users
                # select from users where age=25
                table_name = args[1]
                
                if len(args) > 2 and args[2] == "where":
                    where_str = " ".join(args[3:])
                    where_clause, error = parse_where_condition(where_str)
                    if error:
                        print(f"Ошибка: {error}")
                        continue
                else:
                    where_clause = None
                
                success, result_data = select(metadata, table_name, where_clause)
                if success:
                    if result_data:
                        columns = metadata[table_name]["columns"]
                        display_table(result_data, columns)
                    else:
                        print("Нет данных для отображения")
                else:
                    print(result_data)  # В этом случае result_data содержит сообщение об ошибке
                    
            elif command == "update" and len(args) >= 5 and "set" in args and "where" in args:
                # update users set age=26 where name="John"
                table_name = args[0]
                set_index = args.index("set")
                where_index = args.index("where")
                
                set_str = " ".join(args[set_index+1:where_index])
                where_str = " ".join(args[where_index+1:])
                
                set_clause, set_error = parse_set_clause(set_str)
                where_clause, where_error = parse_where_condition(where_str)
                
                if set_error:
                    print(f"Ошибка в SET: {set_error}")
                    continue
                if where_error:
                    print(f"Ошибка в WHERE: {where_error}")
                    continue
                
                success, message = update(metadata, table_name, set_clause, where_clause)
                print(message)
                
            elif command == "delete" and len(args) >= 4 and args[0] == "from" and args[2] == "where":
                # delete from users where ID=1
                table_name = args[1]
                where_str = " ".join(args[3:])
                
                where_clause, error = parse_where_condition(where_str)
                if error:
                    print(f"Ошибка: {error}")
                    continue
                
                success, message = delete(metadata, table_name, where_clause)
                print(message)
                
            elif command == "info":
                if len(args) != 1:
                    print("Ошибка: Неверное количество аргументов. Используйте: info <имя_таблицы>")
                    continue
                
                table_name = args[0]
                success, message = info(metadata, table_name)
                print(message)
                
            else:
                print(f"Функции '{command}' нет. Попробуйте снова или вызовите справку.")
                
        except KeyboardInterrupt:
            print("\nВыход из программы...")
            break
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            print("Попробуйте снова.")