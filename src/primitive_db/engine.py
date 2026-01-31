import shlex

import prompt

from .core import (
    create_table,
    delete,
    display_table,
    drop_table,
    info,
    insert,
    list_tables,
    select,
    update,
)
from .decorators import handle_db_errors
from .utils import load_metadata, save_metadata


def print_help():
    print()
    print(50*"=")
    print("Справка")
    print(50*"=")

    print("\nРабота с таблицами\n")
    print("create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("drop_table <имя_таблицы> - удалить таблицу")
    print("list_tables - показать список всех таблиц")
    
    print("\nРабота с записями\n")
    print("insert into <имя_таблицы> values "
            "(<значение1>, <значение2>, ...) - создать запись.")
    print("select from <имя_таблицы> " \
            "where <столбец> = <значение> - прочитать записи по условию.")
    print("select from <имя_таблицы> - прочитать все записи.")
    print("update <имя_таблицы> set <столбец1> = <новое_значение1> " \
            "where <столбец_условия> = <значение_условия> - обновить запись.")
    print("delete from <имя_таблицы> where <столбец> = <значение> - удалить запись.")
    print("info <имя_таблицы> - вывести информацию о таблице.")

    print("\nОбщие функции\n")
    print("exit - выйти из программы")
    print("help - справочная информация")  

    print(50*"=")


@handle_db_errors
def run():
    """
    Загружает актуальные метаданные.
    Запрашивает ввод у пользователя.
    Разбирает введенную строку на команду и аргументы.
    После каждой успешной операции сохраняет метаданные.
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
                    print("Ошибка: Недостаточно аргументов. ")
                    print("Используйте: create_table <имя_таблицы> <столбец1:тип> ...")
                    continue
                
                table_name = args[0]
                columns = args[1:]
                
                success, message = create_table(metadata, table_name, columns)
                print(message)
                
                if success:
                    save_metadata(metadata)
                    
            elif command == "drop_table":
                if len(args) != 1:
                    print("Ошибка: Неверное количество аргументов. ")
                    print("Используйте: drop_table <имя_таблицы>")
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
                    
            elif command == "insert" and len(args) >= 4 and args[0] == "into":
                # Ищем индекс "values"
                values_index = -1
                for i, arg in enumerate(args):
                    if arg.lower() == "values":
                        values_index = i
                        break
                
                if values_index == -1:
                    print("Ошибка: Отсутствует ключевое слово 'values'")
                    continue
                
                table_name = args[1]
                
                # Собираем все аргументы после "values" в одну строку
                values_str = " ".join(args[values_index + 1:])
                
                # Парсим значения
                try:
                    values = parse_values_list(values_str)
                except Exception as e:
                    print(f"Ошибка при разборе значений: {e}")
                    continue
                
                success, message = insert(metadata, table_name, values)
                print(message)
                
            elif command == "select" and len(args) >= 2 and args[0] == "from":
                table_name = args[1]
                
                if len(args) > 2 and args[2] == "where":
                    # Собираем все после "where" в одну строку
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
                    # В этом случае result_data содержит сообщение об ошибке
                    print(result_data)  
                    
            elif (command == "update" and len(args) >= 5 
                        and "set" in args and "where" in args):
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
                
                success, message = update(metadata, table_name, 
                                          set_clause, where_clause)
                print(message)
                
            elif (command == "delete" and len(args) >= 4 
                    and args[0] == "from" and args[2] == "where"):
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
                    print("Ошибка: Неверное количество аргументов. " \
                            "Используйте: info <имя_таблицы>")
                    continue
                
                table_name = args[0]
                success, message = info(metadata, table_name)
                print(message)                

            else:
                print(f"Функции '{command}' нет.")
                print("Попробуйте снова или вызовите справку.")
                continue
                
        except KeyboardInterrupt:
            print("\nВыход из программы...")
            break
        except EOFError:
            print("\nВыход из программы...")
            break


def parse_where_condition(where_str):
    """
    Парсит условие WHERE в формате "столбец=значение"
    Возвращает словарь {столбец: значение}
    """
    where_str = where_str.strip()
    
    # Находим первый "=", который не внутри кавычек
    in_quotes = False
    quote_char = None
    equals_index = -1
    
    for i, char in enumerate(where_str):
        if char in ('"', "'") and (i == 0 or where_str[i-1] != '\\'):
            if not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char:
                in_quotes = False
        elif char == '=' and not in_quotes:
            equals_index = i
            break
    
    if equals_index == -1:
        return None, 'Неверный формат условия WHERE. Ожидается: "столбец=значение"'
    
    column = where_str[:equals_index].strip()
    value_str = where_str[equals_index+1:].strip()
    
    # Парсим значение
    success, value = parse_value(value_str)
    if not success:
        return None, value  # здесь value - это сообщение об ошибке
    
    return {column: value}, None


def parse_set_clause(set_str):
    """
    Парсит SET выражение в формате "столбец=значение"
    Возвращает словарь {столбец: значение}
    """
    set_str = set_str.strip()
    
    # Находим первый "=", который не внутри кавычек
    in_quotes = False
    quote_char = None
    equals_index = -1
    
    for i, char in enumerate(set_str):
        if char in ('"', "'") and (i == 0 or set_str[i-1] != '\\'):
            if not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char:
                in_quotes = False
        elif char == '=' and not in_quotes:
            equals_index = i
            break
    
    if equals_index == -1:
        return None, 'Неверный формат SET. Ожидается: "столбец=значение"'
    
    column = set_str[:equals_index].strip()
    value_str = set_str[equals_index+1:].strip()
    
    success, value = parse_value(value_str)
    if not success:
        return None, value
    
    return {column: value}, None


def parse_value(value_str):
    """Парсит строковое значение в соответствующий тип, возвращает (success, value)"""
    value_str = value_str.strip()
    
    # Пустая строка
    if not value_str:
        return False, "Пустое значение"
    
    # Булевы значения
    if value_str.lower() in ('true', 'false'):
        return True, value_str.lower() == 'true'
    
    # Числа (целые и отрицательные)
    try:
        return True, int(value_str)
    except ValueError:
        pass
    
    # Строки (убираем кавычки если есть)
    if (value_str.startswith('"') and value_str.endswith('"')) or \
       (value_str.startswith("'") and value_str.endswith("'")):
        return True, value_str[1:-1]
    
    # Если ничего не подошло, считаем строкой (без кавычек)
    return True, value_str


def parse_values_list(values_str):
    """
    Парсит список значений в формате (value1, value2, value3) 
    или value1, value2, value3
    """
    # Убираем скобки если есть
    values_str = values_str.strip()
    if values_str.startswith("(") and values_str.endswith(")"):
        values_str = values_str[1:-1].strip()
    
    # Если строка пустая после удаления скобок
    if not values_str:
        return []
    
    # Разбиваем строку на отдельные значения
    values = []
    current_value = ""
    in_quotes = False
    quote_char = None
    
    for i, char in enumerate(values_str):
        if char in ('"', "'") and (i == 0 or values_str[i-1] != '\\'):
            if not in_quotes:
                in_quotes = True
                quote_char = char
                current_value += char
            elif char == quote_char:
                in_quotes = False
                current_value += char
            else:
                current_value += char
        elif char == ',' and not in_quotes:
            if current_value.strip():
                success, parsed_val = parse_value(current_value.strip())
                if success:
                    values.append(parsed_val)
                current_value = ""
        else:
            current_value += char
    
    # Добавляем последнее значение
    if current_value.strip():
        success, parsed_val = parse_value(current_value.strip())
        if success:
            values.append(parsed_val)
    
    return values