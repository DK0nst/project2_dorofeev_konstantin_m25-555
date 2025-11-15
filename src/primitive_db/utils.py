import json

def load_metadata(filepath="db_meta.json"):
    """
    Загружает метаданные из JSON-файла.
    Если файл не найден, возвращает пустой словарь.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        print("Ошибка: файл метаданных поврежден.")
        return {}

def save_metadata(data, filepath="db_meta.json"):
    """
    Сохраняет метаданные в JSON-файл.
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Ошибка при сохранении метаданных: {e}")
        return False

def load_table_data(table_name):
    """Загружает данные таблицы из JSON-файла"""
    filepath = f"data/{table_name}.json"
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print(f"Ошибка: не удалось прочитать файл {table_name}.json.")
        return []

def save_table_data(table_name, data):
    """Сохраняет данные таблицы в JSON-файл"""
    # Создаем директорию data, если её нет
    
    filepath = f"data/{table_name}.json"
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)    
        return True
    except Exception as e:
        print(f"Ошибка при сохранении файла: {e}")
        return False