from .utils import save_metadata, load_metadata, load_table_data, save_table_data
from prettytable import PrettyTable

# Поддерживаемые типы данных
SUPPORTED_TYPES = {'int', 'str', 'bool'}

def validate_column_definition(column_def):
    """
    Проверяет корректность определения столбца.
    Формат: "имя:тип"
    """
    if ':' not in column_def:
        return False, f"Некорректный формат столбца: {column_def}. Используйте 'имя:тип'"
    
    name, col_type = column_def.split(':', 1)
    name = name.strip()
    col_type = col_type.strip().lower()
    
    if not name:
        return False, "Имя столбца не может быть пустым"
    
    if col_type not in SUPPORTED_TYPES:
        return False, f"Неподдерживаемый тип данных: {col_type}. Доступные: {', '.join(SUPPORTED_TYPES)}"
    
    return True, (name, col_type)

def create_table(metadata, table_name, columns):

    """
    Создает новую таблицу в метаданных.
    Автоматически добавляет столбец ID:int.
    """
    # Проверяем имя таблицы
    if not table_name or not table_name.strip():
        return False, "Имя таблицы не может быть пустым"

    # Проверяем существование таблицы
    if table_name in metadata:
        return False, f'Таблица "{table_name}" уже существует.'

    # Инициируем новый словарь со столбцом ID
    table_columns = {"ID": "int"}
    
    # Обрабатываем пользовательские столбцы
    for col_def in columns:
        # Проверяем наличие наименования и допустимый тип столбца (обернуто в функцию)
        is_valid, result = validate_column_definition(col_def)
        if not is_valid:
            return False, result
        
        col_name, col_type = result

        # Проверяем дублирование столбцов
        if col_name.upper() == "ID":
            return False, f'Столбец ID зарезервирован за системой и создается автоматически'

        if col_name in table_columns:
            return False, f'Столбец "{col_name}" уже существует в таблице'
        
        table_columns[col_name] = col_type
    
    # Сохраняем таблицу в метаданные
    metadata[table_name] = {"columns": table_columns}
    
    # Формируем сообщение об успехе
    columns_str = ", ".join([f"{name}:{typ}" for name, typ in table_columns.items()])
    return True, f'Таблица "{table_name}" успешно создана со столбцами: {columns_str}'

def drop_table(metadata, table_name):

    """
    Удаляет таблицу из метаданных.
    """

    if table_name not in metadata:
        return False, f'Таблица "{table_name}" не существует.'
    
    del metadata[table_name]
    return True, f'Таблица "{table_name}" успешно удалена.'

def list_tables(metadata):
    """
    Возвращает список всех таблиц.
    """
    if not metadata:
        return "Нет созданных таблиц."
    
    tables = list(metadata.keys())
    if len(tables) == 1:
        return f"- {tables[0]}"
    else:
        return "\n".join([f"- {table}" for table in tables])

# ========== CRUD ОПЕРАЦИИ ==========

def validate_value(value, expected_type):

    """Валидирует значение по типу"""

    if expected_type == "int":
        try:
            return True, int(value)
        except (ValueError, TypeError):
            return False, f'Значение "{value}" не может быть преобразовано в int'
    
    elif expected_type == "bool":
        if isinstance(value, bool):
            return True, value
        value_str = str(value).lower()
        if value_str in ('true', '1', 'yes'):
            return True, True
        elif value_str in ('false', '0', 'no'):
            return True, False
        return False, f'Значение "{value}" не может быть преобразовано в bool'
    
    elif expected_type == "str":
        # Убираем кавычки если есть
        if isinstance(value, str) and len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        return True, str(value)
    
    return False, f'Неизвестный тип: {expected_type}'

def insert(metadata, table_name, values):

    """
    Добавляет новую запись в таблицу
    """
    if table_name not in metadata:
        return False, f'Таблица "{table_name}" не существует'
    
    # Загружаем текущие данные
    table_data = load_table_data(table_name)
    
    # Получаем схему таблицы
    columns = metadata[table_name]["columns"]
    column_names = list(columns.keys())
    
    # Проверяем количество значений (без ID)
    if len(values) != len(column_names) - 1:
        return False, f'Ожидается {len(column_names)-1} значений для полей, получено {len(values)}'

   # Генерируем ID
    if table_data:
        new_id = max(item.get("ID", 0) for item in table_data) + 1
    else:
        new_id = 1

    # Создаем словарь для валидированных данных и сразу добавляем ID
    validated_columns_with_values = {"ID": new_id}

    # Связываем наименования колонок и значения
    columns_with_values_without_id = zip(column_names[1:], values)

    # Валидация значений согласно типу в метаданных
    for col_name, value in columns_with_values_without_id:
        col_type = columns[col_name]

        # Валидация типа
        is_valid, validated_value = validate_value(value, col_type)
        if not is_valid:
            return False, validated_value
        validated_columns_with_values[col_name] = validated_value        
    
    # Добавляем запись
    table_data.append(validated_columns_with_values)
    save_table_data(table_name, table_data)
    
    return True, f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".'

def select(metadata, table_name, where_clause=None):

    """Выбирает записи с возможностью фильтрации"""

    if table_name not in metadata:
        return False, f'Таблица "{table_name}" не существует'
    
    table_data = load_table_data(table_name)
    
    if where_clause is None:
        return True, table_data
    
    # Фильтруем данные
    filtered_data = []
    for record in table_data:
        match = True
        for column, expected_value in where_clause.items():
            if column not in record or record[column] != expected_value:
                match = False
                break
        if match:
            filtered_data.append(record)
    
    return True, filtered_data

def update(metadata, table_name, set_clause, where_clause):

    """Обновляет записи по условию"""

    if table_name not in metadata:
        return False, f'Таблица "{table_name}" не существует'
    
    table_data = load_table_data(table_name)
    updated_count = 0
    
    for record in table_data:
        # Проверяем условие WHERE
        match = True
        for column, expected_value in where_clause.items():
            if column not in record or record[column] != expected_value:
                match = False
                break
        
        if match:
            # Обновляем поля согласно SET
            for column, new_value in set_clause.items():
                if column in record and column != "ID":  # ID нельзя менять
                    # Валидируем новое значение
                    col_type = metadata[table_name]["columns"][column]
                    is_valid, validated_value = validate_value(new_value, col_type)
                    if is_valid:
                        record[column] = validated_value
            updated_count += 1
    
    if updated_count > 0:
        save_table_data(table_name, table_data)
    
    return True, f'Обновлено {updated_count} записей в таблице "{table_name}".'

def delete(metadata, table_name, where_clause):

    """Удаляет записи по условию"""

    if table_name not in metadata:
        return False, f'Таблица "{table_name}" не существует'
    
    table_data = load_table_data(table_name)
    initial_count = len(table_data)
    
    # Фильтруем записи, которые НЕ удовлетворяют условию
    filtered_data = []
    for record in table_data:
        match = True
        for column, expected_value in where_clause.items():
            if column not in record or record[column] != expected_value:
                match = False
                break
        if not match:
            filtered_data.append(record)
    
    deleted_count = initial_count - len(filtered_data)
    
    if deleted_count > 0:
        save_table_data(table_name, filtered_data)
    
    return True, f'Удалено {deleted_count} записей из таблицы "{table_name}".'

def info(metadata, table_name):

    """Выводит информацию о таблице"""

    if table_name not in metadata:
        return False, f'Таблица "{table_name}" не существует'
    
    columns = metadata[table_name]["columns"]
    table_data = load_table_data(table_name)
    
    columns_str = ", ".join([f"{name}:{typ}" for name, typ in columns.items()])
    result = f'Таблица: {table_name}\n'
    result += f'Столбцы: {columns_str}\n'
    result += f'Количество записей: {len(table_data)}'
    
    return True, result

def display_table(data, columns):

    """Выводит данные в виде красивой таблицы с помощью PrettyTable"""

    if not data:
        print("Нет данных для отображения")
        return
    
    table = PrettyTable()
    table.field_names = list(columns.keys())
    
    for record in data:
        row = [record.get(col, "") for col in columns.keys()]
        table.add_row(row)
    
    print(table)

def print_help():

    """
    Выводит справочную информацию.
    """

    print("\n***Операции с данными***")
    print("Функции:")
    print("<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...) - создать запись")
    print("<command> select from <имя_таблицы> [where <столбец>=<значение>] - прочитать записи")
    print("<command> update <имя_таблицы> set <столбец>=<значение> where <столбец>=<значение> - обновить запись")
    print("<command> delete from <имя_таблицы> where <столбец>=<значение> - удалить запись")
    print("<command> info <имя_таблицы> - вывести информацию о таблице")
    print("<command> create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация")
    print("\nВнимание! Разделяйте параметры пробелами, а не запятыми или прочими разделителями!")
    print("Если вы собираетесь использовать в названии таблиц или столбцов пробелы, экранируйте их кавычками.\n")
