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