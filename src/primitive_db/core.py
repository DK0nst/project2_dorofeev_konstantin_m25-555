from .utils import save_metadata, load_metadata

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

    print(name, col_type)
    
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
        if col_name=="ID":
            return False, f'Столбец ID создается зарезервирован за системой и создается автоматически'


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


def print_help():
    """
    Выводит справочную информацию.
    """
    print("\n***База данных***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация")
    print("\nВнимание! Разделяйте параметры пробелами, а не запятыми или прочими разделителями!")
    print("Если вы собираетесь использовать в названии таблиц или столбцов пробелы, экранируйте их кавычками.\n")